import logging
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.auth_service import get_current_user
from database.mongodb import db, resumes_collection
from embeddings.similarity_engine import SimilarityEngine

router = APIRouter()

shortlists_collection = db["shortlists"] if db is not None else None

class ShortlistAddRequest(BaseModel):
    resume_id: str
    notes: Optional[str] = ""

@router.get("/candidates")
async def search_candidates(
    query: Optional[str] = "",
    current_user: dict = Depends(get_current_user)
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
    current_user: dict = Depends(get_current_user)
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
    current_user: dict = Depends(get_current_user)
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

@router.get("/analytics")
async def get_recruiter_analytics(
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        return {"total_resumes": 0, "avg_ats": "0%", "top_skills": []}

    try:
        resumes = list(resumes_collection.find({}))
        total_resumes = len(resumes)
        
        avg_ats = 0
        skills_counter = {}

        if total_resumes > 0:
            avg_ats = int(sum(r.get("ats_score", 0) for r in resumes) / total_resumes)
            for r in resumes:
                for skill in r.get("skills", []):
                    skills_counter[skill] = skills_counter.get(skill, 0) + 1

        top_skills = sorted(skills_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        top_skills_list = [{"skill": s[0], "count": s[1]} for s in top_skills]

        return {
            "total_candidates": total_resumes,
            "avg_ats": f"{avg_ats}%",
            "top_skills": top_skills_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recruiter analytics: {e}")
