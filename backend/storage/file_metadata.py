from bson import ObjectId
from datetime import datetime, timezone
from database.mongodb import resumes_collection

class FileMetadataService:
    @staticmethod
    def create_metadata(
        user_email: str,
        filename: str,
        file_type: str,
        gridfs_file_id: ObjectId,
        ats_score: int = 0,
        skills: list = None,
        parsed_text: str = "",
        category: str = "Others",
        extra_fields: dict = None
    ) -> str:
        if resumes_collection is None:
            raise Exception("Database offline")
        
        doc = {
            "user_email": user_email,
            "filename": filename,
            "file_type": file_type,
            "gridfs_file_id": gridfs_file_id,
            "ats_score": ats_score,
            "semantic_score": ats_score,  # map semantic_score to ats_score
            "category": category,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "date": datetime.now(timezone.utc).isoformat(),  # keep 'date' for backward compatibility
            "skills": skills or [],
            "analysis_status": extra_fields.get("analysis_status", "uploaded") if extra_fields else "uploaded",
            "parsed_text": parsed_text,
            "preview_thumbnail": "",
            "ai_summary": ""
        }
        if extra_fields:
            doc.update(extra_fields)
            
        result = resumes_collection.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_metadata(resume_id: str, user_email: str) -> dict:
        if resumes_collection is None:
            raise Exception("Database offline")
        try:
            doc = resumes_collection.find_one({
                "_id": ObjectId(resume_id),
                "user_email": user_email
            })
            return doc
        except Exception:
            return None

    @staticmethod
    def update_metadata(resume_id: str, user_email: str, update_fields: dict) -> bool:
        if resumes_collection is None:
            raise Exception("Database offline")
        try:
            result = resumes_collection.update_one(
                {"_id": ObjectId(resume_id), "user_email": user_email},
                {"$set": update_fields}
            )
            return result.modified_count > 0
        except Exception:
            return False

    @staticmethod
    def delete_metadata(resume_id: str, user_email: str) -> ObjectId:
        if resumes_collection is None:
            raise Exception("Database offline")
        try:
            doc = resumes_collection.find_one_and_delete({
                "_id": ObjectId(resume_id),
                "user_email": user_email
            })
            if doc and "gridfs_file_id" in doc:
                return doc["gridfs_file_id"]
            return None
        except Exception:
            return None
