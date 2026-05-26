import asyncio
import logging
from bson import ObjectId
from datetime import datetime, timezone

from workers.celery_worker import celery_app
from database.mongodb import resumes_collection, db
from services.extraction_service import extract_text
from services.parsing_engine import parse_resume
from services.scoring_engine import calculate_ats_score
from embeddings.embedding_service import EmbeddingService
from ai.gemini_service import GeminiAIService

logger = logging.getLogger(__name__)
ai_feedback_collection = db["ai_feedback"] if db is not None else None

@celery_app.task
def process_resume_parsing_task(file_path: str, user_email: str, filename: str) -> str:
    """
    Background worker task to extract text, parse section data, 
    and calculate initial ATS scores for uploaded documents.
    """
    logger.info(f"Starting background parse task for file: {filename}")
    try:
        # 1. Perform Text Extraction
        text = extract_text(file_path)

        # 2. Perform Heuristic Resume Parsing
        parsed_data = parse_resume(text)

        # 3. Perform ATS Scoring Calculation
        scoring = calculate_ats_score(parsed_data, text)

        # 4. Compile DB document
        resume_doc = {
            "user_email": user_email,
            "filename": filename,
            "file_path": file_path,
            "parsed_text": text,
            "skills": parsed_data["skills"],
            "education": parsed_data["education"],
            "projects": parsed_data["projects"],
            "experience": parsed_data["experience"],
            "certifications": parsed_data["certifications"],
            "contact": parsed_data["contact"],
            "ats_score": scoring["score"],
            "category_scores": scoring["category_scores"],
            "missing_skills": scoring["missing_skills"],
            "suggestions": scoring["suggestions"],
            "detected_strengths": scoring["detected_strengths"],
            "optimization_recommendations": scoring["optimization_recommendations"],
            "date": datetime.now(timezone.utc).isoformat()
        }

        if resumes_collection is not None:
            result = resumes_collection.insert_one(resume_doc)
            resume_id = str(result.inserted_id)
            
            # Immediately trigger secondary embedding extraction in background
            generate_embeddings_task.delay(resume_id)
            return resume_id
            
        return "Database Offline"
    except Exception as e:
        logger.error(f"Failed parsing background task: {e}")
        raise e

@celery_app.task
def generate_embeddings_task(resume_id_str: str):
    """
    Asynchronously generates and caches text embeddings for the parsed resume.
    """
    logger.info(f"Generating semantic embeddings for resume: {resume_id_str}")
    if resumes_collection is None:
        return "Offline"

    try:
        doc = resumes_collection.find_one({"_id": ObjectId(resume_id_str)})
        if not doc:
            logger.error("Resume record not found for embedding task.")
            return "Not Found"

        # Combine parsed text + found skills for robust semantic context
        text_context = doc.get("parsed_text", "")
        skills_context = " ".join(doc.get("skills", []))
        combined_payload = f"{doc.get('filename', '')} {skills_context} {text_context}"

        # Execute async embedding generation synchronously inside worker task
        async def run_embedding():
            await EmbeddingService.get_embedding(combined_payload)
            
        asyncio.run(run_embedding())
        logger.info(f"Embeddings generated and cached successfully for {resume_id_str}")
        return "Completed"
    except Exception as e:
        logger.error(f"Failed to generate embeddings in background worker: {e}")
        raise e

@celery_app.task
def generate_ai_feedback_task(resume_id_str: str, user_id_str: str, model_name: str, strictness: str):
    """
    Asynchronously triggers Gemini AI review generator and upserts standard collections.
    """
    logger.info(f"Generating background AI feedback for: {resume_id_str}")
    if resumes_collection is None or ai_feedback_collection is None:
        return "Offline"

    try:
        resume = resumes_collection.find_one({"_id": ObjectId(resume_id_str)})
        if not resume:
            return "Resume Not Found"

        resume_data = {
            "filename": resume.get("filename", ""),
            "skills": resume.get("skills", []),
            "education": resume.get("education", []),
            "projects": resume.get("projects", []),
            "experience": resume.get("experience", []),
            "certifications": resume.get("certifications", []),
            "ats_score": resume.get("ats_score", 0),
            "missing_skills": resume.get("missing_skills", [])
        }

        async def run_feedback():
            ai_result = await GeminiAIService.analyze_resume(
                resume_data=resume_data,
                model_name=model_name,
                strictness=strictness
            )
            
            feedback_doc = {
                "resume_id": ObjectId(resume_id_str),
                "user_id": ObjectId(user_id_str) if user_id_str else None,
                "ai_feedback": {
                    "strengths": ai_result.get("strengths", []),
                    "weaknesses": ai_result.get("weaknesses", []),
                    "suggestions": ai_result.get("suggestions", []),
                    "recruiter_feedback": ai_result.get("recruiter_feedback", ""),
                    "career_readiness": ai_result.get("career_readiness", "Intermediate")
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            ai_feedback_collection.update_one(
                {"resume_id": ObjectId(resume_id_str)},
                {"$set": feedback_doc},
                upsert=True
            )

        asyncio.run(run_feedback())
        logger.info(f"AI feedback completed in background for {resume_id_str}")
        return "Completed"
    except Exception as e:
        logger.error(f"AI feedback task failed: {e}")
        raise e
