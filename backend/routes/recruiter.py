import logging
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from database.mongodb import db, resumes_collection
from embeddings.similarity_engine import SimilarityEngine
from middleware.role_guard import RoleGuard

router = APIRouter()

shortlists_collection = db["shortlists"] if db is not None else None
recruiter_jobs_collection = db["recruiter_jobs"] if db is not None else None

logger = logging.getLogger(__name__)

class ShortlistAddRequest(BaseModel):
    resume_id: str
    notes: Optional[str] = ""

class JobPostRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    department: Optional[str] = "Engineering"
    required_skills: Optional[List[str]] = Field(default_factory=list)
    experience_years_required: Optional[int] = 0
    location: Optional[str] = "Remote"

@router.get("/candidates")
async def search_candidates(
    query: Optional[str] = "",
    current_user: dict = Depends(RoleGuard(["recruiter", "admin"]))
):
    if resumes_collection is None:
        return []

    try:
        # Fetch all resumes in the database
        resumes_cursor = resumes_collection.find({})
        all_resumes = []
        for r in resumes_cursor:
            all_resumes.append({
                "id": str(r["_id"]),
                "filename": r.get("filename", ""),
                "user_email": r.get("user_email", ""),
                "skills": r.get("skills", []),
                "ats_score": r.get("ats_score", 0),
                "parsed_text": r.get("parsed_text", ""),
                "experience": r.get("experience", []),
                "education": r.get("education", [])
            })

        if not all_resumes:
            return []

        # 1. Semantic search if query is provided
        if query and query.strip():
            from vector_db.semantic_search import search_candidates_semantic
            try:
                # Use semantic vector db query
                ranked = await search_candidates_semantic(query.strip(), top_k=20)
                return ranked
            except Exception as se_err:
                logger.error(f"Semantic search failed: {se_err}. Falling back to standard matching.")
                
            ranked = await SimilarityEngine.match_query_to_documents(
                query=query.strip(),
                documents=all_resumes,
                text_field="parsed_text",
                top_k=20
            )
            # Remove full parsed_text to save payload network bytes
            for item in ranked:
                item.pop("parsed_text", None)
            return ranked

        # 2. Otherwise return standard sorted by ATS score descending
        all_resumes.sort(key=lambda x: x["ats_score"], reverse=True)
        for item in all_resumes:
            item.pop("parsed_text", None)
        return all_resumes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch candidates: {e}")

@router.post("/shortlist/add")
async def add_candidate_to_shortlist(
    payload: ShortlistAddRequest,
    current_user: dict = Depends(RoleGuard(["recruiter", "admin"]))
):
    if shortlists_collection is None or resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    try:
        # Check if candidate resume exists
        resume = resumes_collection.find_one({"_id": ObjectId(payload.resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="Candidate resume not found.")

        candidate_info = {
            "resume_id": ObjectId(payload.resume_id),
            "filename": resume.get("filename", ""),
            "user_email": resume.get("user_email", ""),
            "ats_score": resume.get("ats_score", 0),
            "added_at": datetime.now(timezone.utc).isoformat(),
            "notes": payload.notes
        }

        # Push to recruiter shortlist (upsert)
        shortlists_collection.update_one(
            {"recruiter_email": current_user["email"]},
            {
                "$push": {"candidates": candidate_info},
                "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )

        return {"message": "Candidate added to shortlist successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to add candidate to shortlist: {e}")

@router.get("/shortlist")
async def get_recruiter_shortlist(
    current_user: dict = Depends(RoleGuard(["recruiter", "admin"]))
):
    if shortlists_collection is None:
        return {"candidates": []}

    try:
        doc = shortlists_collection.find_one({"recruiter_email": current_user["email"]})
        if not doc:
            return {"candidates": []}

        # Convert ObjectIds to strings
        candidates = doc.get("candidates", [])
        for c in candidates:
            c["resume_id"] = str(c["resume_id"])

        return {
            "id": str(doc["_id"]),
            "recruiter_email": doc["recruiter_email"],
            "candidates": candidates,
            "created_at": doc.get("created_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load shortlist: {e}")

@router.post("/jobs")
async def post_recruiter_job(
    payload: JobPostRequest,
    current_user: dict = Depends(RoleGuard(["recruiter", "admin"]))
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    try:
        job_doc = {
            "recruiter_email": current_user["email"],
            "title": payload.title,
            "description": payload.description,
            "department": payload.department,
            "required_skills": payload.required_skills,
            "experience_years_required": payload.experience_years_required,
            "location": payload.location,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db["recruiter_jobs"].insert_one(job_doc)
        job_id_str = str(result.inserted_id)

        # Generate and save vector embedding in background/async
        from vector_db.semantic_search import add_job_vector
        combined_text = f"{payload.title} {payload.department} {payload.description}"
        await add_job_vector(
            job_id_str=job_id_str,
            text=combined_text,
            title=payload.title,
            department=payload.department
        )

        return {
            "message": "Job description posted and indexed successfully.",
            "job_id": job_id_str
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post job: {e}")

@router.get("/jobs")
async def list_recruiter_jobs(
    current_user: dict = Depends(RoleGuard(["recruiter", "admin"]))
):
    if db is None:
        return []

    try:
        jobs_cursor = db["recruiter_jobs"].find({"recruiter_email": current_user["email"]}).sort("created_at", -1)
        results = []
        for doc in jobs_cursor:
            results.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", ""),
                "description": doc.get("description", ""),
                "department": doc.get("department", ""),
                "required_skills": doc.get("required_skills", []),
                "experience_years_required": doc.get("experience_years_required", 0),
                "location": doc.get("location", ""),
                "created_at": doc.get("created_at", "")
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {e}")

@router.get("/analytics")
async def get_recruiter_analytics(
    current_user: dict = Depends(RoleGuard(["recruiter", "admin"]))
):
    if resumes_collection is None:
        return {"total_candidates": 0, "avg_ats": "0%", "top_skills": []}

    try:
        # 1. Pipeline for total count and average ATS score
        stats_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_candidates": {"$sum": 1},
                    "avg_ats": {"$avg": "$ats_score"}
                }
            }
        ]
        
        stats_result = list(resumes_collection.aggregate(stats_pipeline))
        total_candidates = 0
        avg_ats = 0
        
        if stats_result:
            total_candidates = stats_result[0].get("total_candidates", 0)
            avg_ats = int(stats_result[0].get("avg_ats", 0))

        # 2. Pipeline for top skills extraction density mapping
        skills_pipeline = [
            {"$unwind": "$skills"},
            {
                "$group": {
                    "_id": "$skills",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        skills_result = list(resumes_collection.aggregate(skills_pipeline))
        top_skills_list = [{"skill": doc["_id"], "count": doc["count"]} for doc in skills_result]

        return {
            "total_candidates": total_candidates,
            "avg_ats": f"{avg_ats}%",
            "top_skills": top_skills_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recruiter analytics: {e}")
