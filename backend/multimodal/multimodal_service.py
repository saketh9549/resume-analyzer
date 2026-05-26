import logging
from datetime import datetime, timezone
from bson import ObjectId
from database.mongodb import db, resumes_collection
from multimodal.pdf_image_extractor import convert_pdf_to_images
from multimodal.vision_analysis import VisionAnalyzer
from multimodal.layout_scoring import LayoutScorer
from multimodal.readability_engine import ReadabilityEngine

logger = logging.getLogger(__name__)

multimodal_analyses_collection = db["multimodal_analyses"] if db is not None else None

class MultimodalService:
    @classmethod
    async def analyze_resume_visuals(cls, resume_id: str, user_email: str) -> dict:
        """
        Main entry point to perform layout, typography, and visual checks on a PDF resume.
        Saves results in the database and returns them.
        """
        if resumes_collection is None:
            raise RuntimeError("Database connection not initialized.")

        # 1. Fetch resume document
        resume = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": user_email
        })
        if not resume:
            raise FileNotFoundError("Resume record not found or access denied.")

        file_path = resume.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            # Fall back to checking if the file is in uploads directory
            file_path = f"uploads/{resume.get('filename')}"
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Physical file not found at path: {file_path}")

        # 2. Extract first page image from PDF
        images = convert_pdf_to_images(file_path, max_pages=1)
        if not images:
            raise ValueError("Failed to extract pages as images from the PDF document.")
        
        first_page_image = images[0]

        # 3. Call Gemini Vision API
        vision_result = await VisionAnalyzer.analyze_layout_visuals(first_page_image)

        # 4. Run local heuristic checks (readability, text density)
        parsed_data = {
            "skills": resume.get("skills", []),
            "education": resume.get("education", []),
            "experience": resume.get("experience", []),
            "projects": resume.get("projects", [])
        }
        raw_text = resume.get("parsed_text", "")
        
        local_layout = LayoutScorer.calculate_local_layout_scores(parsed_data, raw_text)
        readability = ReadabilityEngine.get_readability_metrics(raw_text)

        # 5. Compile and save results
        analysis_doc = {
            "resume_id": ObjectId(resume_id),
            "user_email": user_email,
            "visual_scores": {
                "layout_score": vision_result.get("layout_score", 75),
                "design_score": vision_result.get("design_score", 70),
                "readability_score": vision_result.get("readability_score", 80),
                "formatting_score": vision_result.get("formatting_score", 75),
                "visual_balance_score": vision_result.get("visual_balance_score", 78),
                "recruiter_readability_score": vision_result.get("recruiter_readability_score", 72),
                "ats_friendliness_score": vision_result.get("ats_friendliness_score", 80),
                "overall_visual_score": vision_result.get("overall_visual_score", 76),
                "local_layout_quality": local_layout.get("local_layout_quality", 75)
            },
            "readability_metrics": readability,
            "layout_feedback": vision_result.get("layout_feedback", ""),
            "design_suggestions": vision_result.get("design_suggestions", []),
            "readability_improvements": vision_result.get("readability_improvements", []),
            "formatting_optimizations": vision_result.get("formatting_optimizations", []),
            "section_ordering_improvements": vision_result.get("section_ordering_improvements", []),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if multimodal_analyses_collection is not None:
            try:
                multimodal_analyses_collection.update_one(
                    {"resume_id": ObjectId(resume_id)},
                    {"$set": analysis_doc},
                    upsert=True
                )
            except Exception as e:
                logger.error(f"Failed to log multimodal analysis to DB: {e}")

        # Convert ObjectIds to strings before returning
        analysis_doc["id"] = str(resume_id)
        analysis_doc["resume_id"] = str(resume_id)
        return analysis_doc
import os
