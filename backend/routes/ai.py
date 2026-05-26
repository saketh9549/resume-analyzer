from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from services.auth_service import get_current_user
from database.mongodb import db, resumes_collection
from ai.gemini_service import GeminiAIService

router = APIRouter()

# Get collection reference, fallback to None if database is offline
ai_feedback_collection = db["ai_feedback"] if db is not None else None

class AIAnalyzeRequest(BaseModel):
    resume_id: str
    model_name: Optional[str] = "gemini-2.5-flash"
    strictness: Optional[str] = "standard"

class RewriteSummaryRequest(BaseModel):
    resume_id: str
    current_summary: Optional[str] = ""

class RecommendSkillsRequest(BaseModel):
    skills: List[str]

@router.post("/analyze")
async def analyze_resume_ai(
    payload: AIAnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline. Cannot execute analysis logging."
        )

    try:
        # Retrieve the resume document
        resume = resumes_collection.find_one({
            "_id": ObjectId(payload.resume_id),
            "user_email": current_user["email"]
        })
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume record not found or access denied."
            )

        # Reconstruct resume context data for Gemini
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

        # Call Gemini service
        ai_result = await GeminiAIService.analyze_resume(
            resume_data=resume_data,
            model_name=payload.model_name,
            strictness=payload.strictness
        )

        # Prepare DB storage document matching Phase 8 Schema
        feedback_doc = {
            "resume_id": ObjectId(payload.resume_id),
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

        # Persist feedback in MongoDB
        if ai_feedback_collection is not None:
            # Upsert so we keep only one review record per resume
            ai_feedback_collection.update_one(
                {"resume_id": ObjectId(payload.resume_id)},
                {"$set": feedback_doc},
                upsert=True
            )

        return {
            "message": "AI analysis completed successfully",
            "ai_feedback": ai_result
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis execution failed: {str(e)}"
        )

@router.get("/feedback/{resume_id}")
async def get_ai_feedback(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if ai_feedback_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline."
        )

    try:
        # Retrieve stored feedback matching this resume
        doc = ai_feedback_collection.find_one({"resume_id": ObjectId(resume_id)})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI feedback not found for this resume. Trigger /ai/analyze first."
            )
        
        # Verify access credentials (check if resume belongs to user)
        resume = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this resume feedback is denied."
            )

        # Convert ObjectIds to strings for API payload serialization
        return {
            "id": str(doc["_id"]),
            "resume_id": str(doc["resume_id"]),
            "ai_feedback": doc["ai_feedback"],
            "generated_at": doc["generated_at"]
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve AI feedback: {str(e)}"
        )

@router.post("/rewrite-summary")
async def rewrite_resume_summary(
    payload: RewriteSummaryRequest,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline."
        )

    try:
        resume = resumes_collection.find_one({
            "_id": ObjectId(payload.resume_id),
            "user_email": current_user["email"]
        })
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume record not found."
            )

        resume_data = {
            "skills": resume.get("skills", []),
            "experience": resume.get("experience", []),
            "projects": resume.get("projects", [])
        }

        rewritten = await GeminiAIService.rewrite_summary(
            resume_data=resume_data,
            current_summary=payload.current_summary
        )

        return rewritten
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary rewrite failed: {str(e)}"
        )

@router.post("/recommend-skills")
async def recommend_next_skills(
    payload: RecommendSkillsRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        recommendations = await GeminiAIService.recommend_skills(skills=payload.skills)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skills recommendations failed: {str(e)}"
        )
