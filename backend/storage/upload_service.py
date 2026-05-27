import os
import tempfile
from bson import ObjectId
from storage.gridfs_service import GridFSService
from storage.file_metadata import FileMetadataService
from services.extraction_service import extract_text
from services.parsing_engine import parse_resume
from services.scoring_engine import calculate_ats_score

class UploadService:
    @staticmethod
    async def upload_only_resume(
        file_bytes: bytes,
        filename: str,
        content_type: str,
        user_email: str
    ) -> dict:
        # 1. Save file to GridFS
        file_type = content_type or "application/pdf"
        gridfs_file_id = GridFSService.save_file(file_bytes, filename, file_type)

        # 2. Save metadata with "uploaded" status, and empty parser fields
        extra_fields = {
            "analysis_status": "uploaded",
            "education": [],
            "projects": [],
            "experience": [],
            "certifications": [],
            "contact": {},
            "category_scores": {},
            "missing_skills": [],
            "suggestions": [],
            "detected_strengths": [],
            "optimization_recommendations": []
        }

        resume_id = FileMetadataService.create_metadata(
            user_email=user_email,
            filename=filename,
            file_type=file_type,
            gridfs_file_id=gridfs_file_id,
            ats_score=0,
            skills=[],
            parsed_text="",
            category="Others",
            extra_fields=extra_fields
        )

        return {
            "id": resume_id,
            "filename": filename,
            "analysis_status": "uploaded",
            "score": 0
        }

    @staticmethod
    async def upload_and_process_resume(
        file_bytes: bytes,
        filename: str,
        content_type: str,
        user_email: str
    ) -> dict:
        # 1. Save file to GridFS
        file_type = content_type or "application/pdf"
        gridfs_file_id = GridFSService.save_file(file_bytes, filename, file_type)

        # 2. Save file temporarily to disk to run text extraction (compatible with parser engines)
        suffix = os.path.splitext(filename)[1].lower()
        temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(temp_file_fd, 'wb') as temp_file:
                temp_file.write(file_bytes)

            # 3. Perform text extraction
            text = extract_text(temp_file_path)
        finally:
            # Clean up temp file immediately
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                print(f"Error removing temp file: {e}")

        # 4. Perform Heuristic Resume Parsing
        parsed_data = parse_resume(text)

        # 5. Perform ATS Scoring Calculation
        scoring = calculate_ats_score(parsed_data, text)

        # 6. Save metadata
        extra_fields = {
            "education": parsed_data["education"],
            "projects": parsed_data["projects"],
            "experience": parsed_data["experience"],
            "certifications": parsed_data["certifications"],
            "contact": parsed_data["contact"],
            "category_scores": scoring["category_scores"],
            "missing_skills": scoring["missing_skills"],
            "suggestions": scoring["suggestions"],
            "detected_strengths": scoring["detected_strengths"],
            "optimization_recommendations": scoring["optimization_recommendations"]
        }

        resume_id = FileMetadataService.create_metadata(
            user_email=user_email,
            filename=filename,
            file_type=file_type,
            gridfs_file_id=gridfs_file_id,
            ats_score=scoring["score"],
            skills=parsed_data["skills"],
            parsed_text=text,
            category="Others",
            extra_fields=extra_fields
        )

        return {
            "id": resume_id,
            "filename": filename,
            "score": scoring["score"],
            "skills_found": parsed_data["skills"],
            "missing_skills": scoring["missing_skills"],
            "suggestions": scoring["suggestions"],
            "detected_strengths": scoring["detected_strengths"],
            "optimization_recommendations": scoring["optimization_recommendations"],
            "category_scores": scoring["category_scores"],
            "education": parsed_data["education"],
            "experience": parsed_data["experience"],
            "projects": parsed_data["projects"],
            "certifications": parsed_data["certifications"],
            "contact": parsed_data["contact"]
        }
