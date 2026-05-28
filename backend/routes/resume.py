from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    status,
    Request,
    WebSocket,
    WebSocketDisconnect
)
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import shutil
import os
import json
import asyncio
from datetime import datetime, timezone
from bson import ObjectId
from services.auth_service import get_current_user, oauth2_scheme
from services.extraction_service import extract_text
from services.parsing_engine import parse_resume
from services.scoring_engine import calculate_ats_score
from database.mongodb import resumes_collection, db
from multimodal.multimodal_service import MultimodalService

# GridFS Storage Services
from storage.gridfs_service import GridFSService
from storage.file_metadata import FileMetadataService
from storage.upload_service import UploadService
from storage.download_service import DownloadService
from storage.preview_service import PreviewService

# Celery Worker Tasks
from workers.celery_worker import is_redis_available
from workers.tasks import run_async_analysis_task
from workers.redis_config import get_redis_client

router = APIRouter()

class RenameRequest(BaseModel):
    name: str

async def get_current_user_optional_query(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> dict:
    if not token:
        # Fallback to query parameter if Authorization header is not set
        token = request.query_params.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in."
        )
    return get_current_user(token)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        file_bytes = await file.read()
        
        # 1. Validate File Size limit (5MB)
        max_size = 5 * 1024 * 1024 # 5MB
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds the maximum limit of 5MB."
            )

        # 2. Validate MIME Type / File Extension
        allowed_extensions = {".pdf", ".docx", ".doc"}
        allowed_content_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "application/octet-stream" # some clients map PDF/Doc to octet-stream
        }
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions and file.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Only PDF, DOC, and DOCX documents are accepted."
            )

        res = await UploadService.upload_only_resume(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type,
            user_email=current_user["email"]
        )
        return {
            "message": "Resume uploaded successfully",
            **res
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/list")
async def list_resumes(
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline"
        )
    # Projection: only fetch the lightweight fields needed — exclude heavy text/embedding blobs
    _LIST_PROJECTION = {
        "filename": 1, "ats_score": 1, "upload_date": 1,
        "date": 1, "category": 1, "analysis_status": 1
    }
    try:
        cursor = resumes_collection.find(
            {"user_email": current_user["email"]},
            _LIST_PROJECTION
        ).sort("upload_date", -1)
        results = []
        for doc in cursor:
            results.append({
                "id": str(doc["_id"]),
                "name": doc.get("filename", ""),
                "score": f"{doc.get('ats_score', 0)}%",
                "date": (doc.get("upload_date") or doc.get("date") or "")[:10],
                "category": doc.get("category", "Others"),
                "analysis_status": doc.get("analysis_status", "analyzed")
            })
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list resumes: {str(e)}"
        )

@router.get("/user")
async def get_user_resumes(
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline"
        )
    _LIST_PROJECTION = {
        "filename": 1, "ats_score": 1, "upload_date": 1,
        "date": 1, "category": 1, "analysis_status": 1
    }
    try:
        cursor = resumes_collection.find(
            {"user_email": current_user["email"]},
            _LIST_PROJECTION
        ).sort("upload_date", -1)
        results = []
        for doc in cursor:
            results.append({
                "id": str(doc["_id"]),
                "name": doc.get("filename", ""),
                "score": f"{doc.get('ats_score', 0)}%",
                "date": (doc.get("upload_date") or doc.get("date") or "")[:10],
                "category": doc.get("category", "Others"),
                "analysis_status": doc.get("analysis_status", "analyzed")
            })
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list resumes: {str(e)}"
        )

@router.get("/recent")
async def get_recent_resumes(
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service offline."
        )

    _RECENT_PROJECTION = {
        "filename": 1, "ats_score": 1, "upload_date": 1,
        "date": 1, "analysis_status": 1
    }
    try:
        cursor = resumes_collection.find(
            {"user_email": current_user["email"]},
            _RECENT_PROJECTION
        ).sort("upload_date", -1).limit(10)
        results = []
        for doc in cursor:
            score_val = doc.get("ats_score", 0)
            try:
                if isinstance(score_val, str):
                    score_val = int(score_val.replace("%", "").strip())
                else:
                    score_val = int(score_val)
            except:
                score_val = 0

            results.append({
                "resume_id": str(doc["_id"]),
                "name": doc["filename"],
                "ats_score": score_val,
                "id": str(doc["_id"]),
                "score": f"{score_val}%",
                "date": (doc.get("upload_date") or doc.get("date") or "")[:10],
                "analysis_status": doc.get("analysis_status", "analyzed")
            })
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch uploads: {str(e)}"
        )

@router.get("/stats")
async def get_resume_stats(
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service offline."
        )

    try:
        user_email = current_user["email"]

        # ── Single aggregation pipeline replaces all Python-side loops ──────
        # Stage 1: filter by user, Stage 2: unwind skills for counting,
        # Stage 3: group everything in one DB round-trip.
        pipeline = [
            {"$match": {"user_email": user_email}},
            {"$facet": {
                # Sub-pipeline A: aggregate-level stats
                "summary": [
                    {"$group": {
                        "_id": None,
                        "count": {"$sum": 1},
                        "avg_ats": {"$avg": {"$ifNull": ["$ats_score", 0]}},
                        "latest_date": {"$max": {"$ifNull": ["$upload_date", ""]}},
                        "unique_skills": {"$addToSet": "$skills"}
                    }}
                ],
                # Sub-pipeline B: top skills by frequency
                "top_skills_pipe": [
                    {"$match": {"skills": {"$exists": True, "$type": "array"}}},
                    {"$unwind": "$skills"},
                    {"$match": {"skills": {"$ne": None, "$ne": ""}}},
                    {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ]
            }}
        ]

        agg_result = list(resumes_collection.aggregate(pipeline))
        facet = agg_result[0] if agg_result else {}

        summary_docs = facet.get("summary", [])
        top_skills_docs = facet.get("top_skills_pipe", [])

        summary = summary_docs[0] if summary_docs else {}
        total_uploads = summary.get("count", 0)
        avg_score = int(summary.get("avg_ats", 0))
        latest_date_raw = summary.get("latest_date", "")
        latest_date = latest_date_raw[:10] if latest_date_raw else "N/A"

        # Flatten nested skill arrays from $addToSet of arrays
        nested_skills = summary.get("unique_skills", [])
        all_unique_skills = set()
        for item in nested_skills:
            if isinstance(item, list):
                all_unique_skills.update(s for s in item if s)
            elif isinstance(item, str) and item:
                all_unique_skills.add(item)
        skills_found_count = len(all_unique_skills)

        top_skills = [doc["_id"] for doc in top_skills_docs if doc.get("_id")]
        job_matches = max(1, int(avg_score / 10)) if total_uploads > 0 else 0

        return {
            "total_resumes": total_uploads,
            "average_ats_score": avg_score,
            "top_skills": top_skills,
            "latest_upload": latest_date,
            "avg_score": f"{avg_score}%",
            "skills_found": str(skills_found_count),
            "job_matches": str(job_matches),
            "total_uploads": str(total_uploads)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate stats: {str(e)}"
        )

@router.get("/analytics")
async def get_resume_analytics(
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service offline."
        )

    _ANALYTICS_PROJECTION = {
        "filename": 1, "ats_score": 1, "upload_date": 1, "date": 1
    }
    try:
        cursor = resumes_collection.find(
            {"user_email": current_user["email"]},
            _ANALYTICS_PROJECTION
        ).sort("upload_date", 1).limit(7)
        results = []

        for doc in cursor:
            date_str = doc.get("upload_date") or doc.get("date") or ""
            day_label = date_str[:10]
            try:
                parsed_date = datetime.fromisoformat(date_str)
                day_label = parsed_date.strftime("%a")
            except:
                pass
            
            score_val = doc.get("ats_score", 0)
            try:
                if isinstance(score_val, str):
                    score_val = int(score_val.replace("%", "").strip())
                else:
                    score_val = int(score_val)
            except:
                score_val = 0

            results.append({
                "name": f"{day_label} ({doc['filename']})",
                "score": score_val
            })

        if not results:
            results = [
                {"name": "No Data", "score": 0}
            ]
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )

@router.get("/{resume_id}")
async def get_resume_by_id(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline"
        )
    try:
        if not ObjectId.is_valid(resume_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resume ID format."
            )
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume record not found."
            )
        return {
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "skills": doc.get("skills", []),
            "education": doc.get("education", []),
            "experience": doc.get("experience", []),
            "projects": doc.get("projects", []),
            "certifications": doc.get("certifications", []),
            "contact": doc.get("contact", {}),
            "ats_score": doc.get("ats_score", 0),
            "category_scores": doc.get("category_scores", {}),
            "missing_skills": doc.get("missing_skills", []),
            "suggestions": doc.get("suggestions", []),
            "detected_strengths": doc.get("detected_strengths", []),
            "optimization_recommendations": doc.get("optimization_recommendations", []),
            "extracted_entities": doc.get("extracted_entities", {}),
            "ats_breakdown": doc.get("ats_breakdown", []),
            "feedback_history": doc.get("feedback_history", {}),
            "section_confidences": doc.get("section_confidences", {}),
            "section_diagnostics": doc.get("section_diagnostics", {}),
            "extracted_skills": doc.get("extracted_skills", doc.get("skills", [])),
            "semantic_tags": doc.get("semantic_tags", []),
            "recruiter_score": doc.get("recruiter_score", 0),
            "interview_topics": doc.get("interview_topics", []),
            "ai_context": doc.get("ai_context", {}),
            "embeddings": doc.get("embeddings", {}),
            "ats_weaknesses": doc.get("ats_weaknesses", doc.get("missing_skills", [])),
            "upload_date": doc.get("upload_date")
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume: {str(e)}"
        )

@router.get("/preview/{resume_id}")
async def preview_resume_endpoint(
    resume_id: str,
    current_user: dict = Depends(get_current_user_optional_query)
):
    return PreviewService.preview_resume(resume_id, current_user["email"])

@router.get("/download/{resume_id}")
@router.get("/{resume_id}/download")
async def download_resume_endpoint(
    resume_id: str,
    current_user: dict = Depends(get_current_user_optional_query)
):
    return DownloadService.download_resume(resume_id, current_user["email"])

@router.get("/parse/{resume_id}")
async def get_parsed_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline"
        )
    
    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume record not found."
            )
            
        return {
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "skills": doc.get("skills", []),
            "education": doc.get("education", []),
            "experience": doc.get("experience", []),
            "projects": doc.get("projects", []),
            "certifications": doc.get("certifications", []),
            "contact": doc.get("contact", {}),
            "ats_score": doc.get("ats_score", 0),
            "category_scores": doc.get("category_scores", {}),
            "missing_skills": doc.get("missing_skills", []),
            "suggestions": doc.get("suggestions", []),
            "detected_strengths": doc.get("detected_strengths", []),
            "optimization_recommendations": doc.get("optimization_recommendations", []),
            "extracted_entities": doc.get("extracted_entities", {}),
            "ats_breakdown": doc.get("ats_breakdown", []),
            "feedback_history": doc.get("feedback_history", {}),
            "section_confidences": doc.get("section_confidences", {}),
            "section_diagnostics": doc.get("section_diagnostics", {})
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch parsed resume: {str(e)}"
        )

@router.get("/ats/{resume_id}")
async def get_ats_score_breakdown(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline"
        )
        
    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume record not found."
            )
            
        return {
            "id": str(doc["_id"]),
            "ats_score": doc.get("ats_score", 0),
            "category_scores": doc.get("category_scores", {}),
            "missing_skills": doc.get("missing_skills", []),
            "suggestions": doc.get("suggestions", []),
            "ats_breakdown": doc.get("ats_breakdown", []),
            "feedback_history": doc.get("feedback_history", {})
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ATS breakdown: {str(e)}"
        )



@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        # 1. Delete physical file on disk (backward compatibility if any old local files exist)
        file_path = doc.get("file_path", "")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as fe:
                print(f"Failed to delete physical file: {fe}")

        # 2. Delete from GridFS
        gridfs_file_id = doc.get("gridfs_file_id")
        if gridfs_file_id:
            GridFSService.delete_file(ObjectId(gridfs_file_id))

        # 3. Delete metadata
        FileMetadataService.delete_metadata(resume_id, current_user["email"])

        # 4. Cascaded cleanups of linked collections to prevent DB bloat
        if db is not None:
            db["ai_feedback"].delete_many({"resume_id": ObjectId(resume_id)})
            db["job_matches"].delete_many({"resume_id": ObjectId(resume_id)})
            db["interview_sessions"].delete_many({"resume_id": ObjectId(resume_id)})
            db["rewrite_history"].delete_many({"resume_id": ObjectId(resume_id)})
            db["multimodal_analyses"].delete_many({"resume_id": ObjectId(resume_id)})

        return {"message": "Resume and linked insights deleted successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.put("/{resume_id}/rename")
@router.patch("/{resume_id}/rename")
@router.patch("/rename/{resume_id}")
async def rename_resume(
    resume_id: str,
    payload: RenameRequest,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        # Update filename in MongoDB
        FileMetadataService.update_metadata(resume_id, current_user["email"], {"filename": payload.name})

        return {"message": "Resume renamed successfully", "name": payload.name}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")

@router.post("/{resume_id}/reanalyze")
async def reanalyze_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        # Fetch bytes from GridFS and write to temp file
        gridfs_file_id = doc.get("gridfs_file_id")
        file_path = doc.get("file_path", "")
        temp_file_path = None

        if gridfs_file_id:
            import tempfile
            try:
                file_bytes = GridFSService.read_file(ObjectId(gridfs_file_id))
                suffix = os.path.splitext(doc.get("filename", ".pdf"))[1].lower()
                temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(temp_file_fd, 'wb') as temp_file:
                    temp_file.write(file_bytes)
                file_path = temp_file_path
            except Exception as e:
                print(f"Failed to fetch file from GridFS for re-analysis: {e}")

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Physical file missing.")

        try:
            # Re-run extraction, parsing, and scoring pipeline
            text = extract_text(file_path)
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    print(f"Failed to delete temp file: {e}")

        parsed_data = parse_resume(text)
        scoring = calculate_ats_score(parsed_data, text)

        # Update Mongo document
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
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
                "upload_date": datetime.now(timezone.utc).isoformat()
            }}
        )

        return {
            "message": "Resume reanalyzed successfully",
            "id": resume_id,
            "score": scoring["score"],
            "skills_found": parsed_data["skills"]
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Re-analysis failed: {str(e)}")

@router.post("/{resume_id}/analyze")
async def analyze_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        # 1. Retrieve the resume
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        # 2. Check if Celery/Redis is available for background processing
        if is_redis_available():
            # Update status to 'queued' in MongoDB
            resumes_collection.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": {
                    "analysis_status": "queued",
                    "progress": 5,
                    "progress_message": "Resume analysis task queued in background."
                }}
            )
            # Dispatch Celery background task
            run_async_analysis_task.delay(resume_id, current_user["email"])
            return {
                "message": "Analysis Started",
                "id": resume_id,
                "analysis_status": "queued",
                "score": 0
            }

        # Otherwise fall back to synchronous inline processing:
        # 2. Update status to 'processing'
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
                "analysis_status": "processing",
                "ats_score": 0
            }}
        )

        gridfs_file_id = doc.get("gridfs_file_id")
        file_path = doc.get("file_path", "")
        temp_file_path = None

        if gridfs_file_id:
            import tempfile
            try:
                file_bytes = GridFSService.read_file(ObjectId(gridfs_file_id))
                suffix = os.path.splitext(doc.get("filename", ".pdf"))[1].lower()
                temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(temp_file_fd, 'wb') as temp_file:
                    temp_file.write(file_bytes)
                file_path = temp_file_path
            except Exception as e:
                print(f"Failed to fetch file from GridFS for analysis: {e}")

        if not file_path or not os.path.exists(file_path):
            resumes_collection.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": {"analysis_status": "failed"}}
            )
            raise HTTPException(status_code=404, detail="Physical file missing.")

        try:
            # 3. Extract text
            text = extract_text(file_path)
        except Exception as e:
            resumes_collection.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": {"analysis_status": "failed"}}
            )
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    print(f"Failed to delete temp file: {e}")

        # 4. Parse resume & score
        parsed_data = parse_resume(text)
        scoring = calculate_ats_score(parsed_data, text)

        # 5. Update resumes_collection with parsing & ATS results
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
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
            }}
        )

        # 6. Run AI Recruiter feedback analysis
        from ai.gemini_service import GeminiAIService
        resume_data = {
            "filename": doc.get("filename", ""),
            "skills": parsed_data["skills"],
            "education": parsed_data["education"],
            "projects": parsed_data["projects"],
            "experience": parsed_data["experience"],
            "certifications": parsed_data["certifications"],
            "ats_score": scoring["score"],
            "missing_skills": scoring["missing_skills"]
        }

        model_name = "gemini-2.5-flash"
        strictness = "standard"
        ai_result = await GeminiAIService.analyze_resume(
            resume_data=resume_data,
            model_name=model_name,
            strictness=strictness
        )

        # Persist feedback in MongoDB
        feedback_doc = {
            "resume_id": ObjectId(resume_id),
            "user_id": ObjectId(current_user["id"]) if "id" in current_user else None,
            "ai_feedback": {
                "strengths": ai_result.get("strengths", []),
                "weaknesses": ai_result.get("weaknesses", []),
                "suggestions": ai_result.get("suggestions", []),
                "recruiter_feedback": ai_result.get("recruiter_feedback", ""),
                "career_readiness": ai_result.get("career_readiness", "Intermediate")
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        if db is not None:
            db["ai_feedback"].update_one(
                {"resume_id": ObjectId(resume_id)},
                {"$set": feedback_doc},
                upsert=True
            )

        # 7. Run Multimodal vision layout audit (only if it's a PDF)
        multimodal_result = None
        if doc.get("filename", "").lower().endswith(".pdf"):
            try:
                multimodal_result = await MultimodalService.analyze_resume_visuals(resume_id, current_user["email"])
            except Exception as me:
                print(f"Multimodal analysis skipped or failed: {me}")

        # 8. Set status to 'analyzed' and save final timestamps
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
                "analysis_status": "analyzed",
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }}
        )

        return {
            "message": "Resume analyzed successfully",
            "id": resume_id,
            "analysis_status": "analyzed",
            "ats_score": scoring["score"],
            "parsed_data": {
                "skills": parsed_data["skills"],
                "education": parsed_data["education"],
                "experience": parsed_data["experience"],
                "projects": parsed_data["projects"],
                "certifications": parsed_data["certifications"],
                "contact": parsed_data["contact"],
                "category_scores": scoring["category_scores"],
                "missing_skills": scoring["missing_skills"],
                "suggestions": scoring["suggestions"],
                "detected_strengths": scoring["detected_strengths"],
                "optimization_recommendations": scoring["optimization_recommendations"],
            },
            "ai_feedback": ai_result,
            "multimodal_analysis": multimodal_result
        }

    except Exception as e:
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {"analysis_status": "failed"}}
        )
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{resume_id}/analysis-results")
async def get_analysis_results(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        # 1. Fetch resume document
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        # 2. Fetch AI feedback
        ai_feedback_doc = None
        if db is not None:
            ai_feedback_doc = db["ai_feedback"].find_one({"resume_id": ObjectId(resume_id)})

        # 3. Fetch multimodal audit
        multimodal_doc = None
        if db is not None:
            multimodal_doc = db["multimodal_analyses"].find_one({"resume_id": ObjectId(resume_id)})
            if multimodal_doc:
                # Convert ObjectId to string
                multimodal_doc["id"] = str(multimodal_doc["_id"])
                multimodal_doc["resume_id"] = str(multimodal_doc["resume_id"])
                del multimodal_doc["_id"]

        # 4. Construct unified return
        return {
            "message": "Resume analysis retrieved successfully",
            "id": resume_id,
            "analysis_status": doc.get("analysis_status", "analyzed"),
            "ats_score": doc.get("ats_score", 0),
            "parsed_data": {
                "skills": doc.get("skills", []),
                "education": doc.get("education", []),
                "experience": doc.get("experience", []),
                "projects": doc.get("projects", []),
                "certifications": doc.get("certifications", []),
                "contact": doc.get("contact", {}),
                "category_scores": doc.get("category_scores", {}),
                "missing_skills": doc.get("missing_skills", []),
                "suggestions": doc.get("suggestions", []),
                "detected_strengths": doc.get("detected_strengths", []),
                "optimization_recommendations": doc.get("optimization_recommendations", []),
            },
            "ai_feedback": ai_feedback_doc.get("ai_feedback") if ai_feedback_doc else None,
            "multimodal_analysis": multimodal_doc
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis results: {str(e)}")

@router.post("/{resume_id}/multimodal-analyze")
async def multimodal_analyze(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        result = await MultimodalService.analyze_resume_visuals(resume_id, current_user["email"])
        return result
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multimodal vision audit failed: {str(e)}")


@router.websocket("/ws/analysis/{resume_id}")
async def websocket_analysis_endpoint(websocket: WebSocket, resume_id: str):
    await websocket.accept()
    
    if resumes_collection is None:
        await websocket.send_json({"status": "failed", "progress": 0, "message": "Database offline."})
        await websocket.close()
        return

    if not ObjectId.is_valid(resume_id):
        await websocket.send_json({"status": "failed", "progress": 0, "message": "Invalid resume ID format."})
        await websocket.close()
        return

    try:
        doc = resumes_collection.find_one({"_id": ObjectId(resume_id)})
        if not doc:
            await websocket.send_json({"status": "failed", "progress": 0, "message": "Resume record not found."})
            await websocket.close()
            return
            
        current_status = doc.get("analysis_status", "uploaded")
        current_progress = doc.get("progress", 0)
        current_message = doc.get("progress_message", "Initializing...")

        if current_status in ["completed", "analyzed", "failed"]:
            await websocket.send_json({
                "status": current_status,
                "progress": 100 if current_status in ["completed", "analyzed"] else current_progress,
                "message": current_message
            })
            await websocket.close()
            return

        await websocket.send_json({
            "status": current_status,
            "progress": current_progress,
            "message": current_message
        })

        if is_redis_available():
            r = get_redis_client()
            pubsub = r.pubsub()
            pubsub.subscribe(f"analysis_channel_{resume_id}")

            try:
                while True:
                    msg = pubsub.get_message(ignore_subscribe_messages=True)
                    if msg:
                        data = json.loads(msg["data"])
                        await websocket.send_json(data)
                        if data.get("status") in ["completed", "analyzed", "failed"]:
                            break
                    await asyncio.sleep(0.5)
            except WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"Error in Redis pub/sub websocket loop: {e}")
            finally:
                try:
                    pubsub.unsubscribe(f"analysis_channel_{resume_id}")
                except Exception:
                    pass
        else:
            try:
                last_status = current_status
                last_progress = current_progress
                while True:
                    await asyncio.sleep(1.0)
                    fresh_doc = resumes_collection.find_one({"_id": ObjectId(resume_id)})
                    if not fresh_doc:
                        break
                    
                    status_now = fresh_doc.get("analysis_status", "uploaded")
                    progress_now = fresh_doc.get("progress", 0)
                    msg_now = fresh_doc.get("progress_message", "Processing...")

                    if status_now != last_status or progress_now > last_progress:
                        await websocket.send_json({
                            "status": status_now,
                            "progress": progress_now,
                            "message": msg_now
                        })
                        last_status = status_now
                        last_progress = progress_now
                        
                    if status_now in ["completed", "analyzed", "failed"]:
                        break
            except WebSocketDisconnect:
                pass
            except Exception as e:
                print(f"Error in polling websocket fallback: {e}")

    except Exception as e:
        print(f"WebSocket execution error: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass