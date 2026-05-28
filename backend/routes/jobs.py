from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from services.auth_service import get_current_user
from database.mongodb import db, resumes_collection
from jobs.job_matcher import JobMatcherCoordinator
from jobs.scoring_engine import ScoringEngine
from jobs.recommendation_engine import JobRecommendationEngine
from jobs.skill_matcher import SkillMatcher


router = APIRouter()

# Get collection reference, fallback to None if database is offline
job_matches_collection = db["job_matches"] if db is not None else None

class JobMatchRequest(BaseModel):
    resume_id: str
    preferred_industries: Optional[List[str]] = Field(default_factory=list)
    preferred_roles: Optional[List[str]] = Field(default_factory=list)
    experience_level: Optional[str] = ""
    location_preference: Optional[str] = ""

class CustomJDMatchRequest(BaseModel):
    resume_id: str
    job_title: str
    job_description: str
    experience_level: Optional[str] = "Intermediate"
    experience_years_required: Optional[int] = 2
    required_skills: Optional[List[str]] = Field(default_factory=list)
    industry: Optional[str] = "Software Engineering"
    salary_range: Optional[str] = "N/A"

@router.post("/match")
async def match_resume_jobs(
    payload: JobMatchRequest,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline. Cannot execute job matching."
        )

    if not ObjectId.is_valid(payload.resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
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

        resume_data = {
            "skills": resume.get("skills", []),
            "education": resume.get("education", []),
            "projects": resume.get("projects", []),
            "experience": resume.get("experience", []),
            "certifications": resume.get("certifications", []),
            "ats_score": resume.get("ats_score", 0)
        }

        preferences = {
            "preferred_industries": payload.preferred_industries,
            "preferred_roles": payload.preferred_roles,
            "experience_level": payload.experience_level,
            "location_preference": payload.location_preference
        }

        # Run coordinator matching
        match_result = await JobMatcherCoordinator.match_resume_to_jobs(
            resume_data=resume_data,
            preferences=preferences
        )

        # Prepare DB storage document
        match_doc = {
            "resume_id": ObjectId(payload.resume_id),
            "user_email": current_user["email"],
            "user_id": ObjectId(current_user["id"]) if "id" in current_user else None,
            "recommended_jobs": match_result["recommended_jobs"],
            "career_guidance": match_result["career_guidance"],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        # Persist feedback in MongoDB
        if job_matches_collection is not None:
            # Upsert matching document
            job_matches_collection.update_one(
                {"resume_id": ObjectId(payload.resume_id)},
                {"$set": match_doc},
                upsert=True
            )

        return {
            "message": "Job matching evaluation completed successfully",
            "recommended_jobs": match_result["recommended_jobs"],
            "career_guidance": match_result["career_guidance"]
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job matching execution failed: {str(e)}"
        )

@router.get("/recommend/{resume_id}")
async def get_recommended_jobs(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if job_matches_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline."
        )

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        # Verify access credentials and resume existence first
        resume = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume record not found."
            )

        # Retrieve stored matching details
        doc = job_matches_collection.find_one({"resume_id": ObjectId(resume_id)})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommended jobs not found. Trigger /jobs/match first."
            )

        recommended_jobs = doc.get("recommended_jobs", [])
        career_guidance = doc.get("career_guidance", {})
        
        # Calculate semantic score fallback
        semantic_score = 82
        if "overall_score" in career_guidance:
            semantic_score = career_guidance["overall_score"]
        elif "semantic_alignment_score" in career_guidance:
            semantic_score = career_guidance["semantic_alignment_score"]
        elif recommended_jobs:
            avg_matches = sum(j.get("match_percentage", 0) for j in recommended_jobs) / len(recommended_jobs)
            semantic_score = int(avg_matches)

        recommended_roles = [j.get("job_title") for j in recommended_jobs if j.get("job_title")]

        return {
            "id": str(doc["_id"]),
            "resume_id": str(doc["resume_id"]),
            "recommended_jobs": recommended_jobs,
            "career_guidance": career_guidance,
            "generated_at": doc["generated_at"],
            "matches": recommended_jobs,
            "semantic_score": semantic_score,
            "recommended_roles": recommended_roles
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recommended jobs: {str(e)}"
        )

@router.post("/match-custom")
async def match_custom_jd(
    payload: CustomJDMatchRequest,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline."
        )

    if not ObjectId.is_valid(payload.resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
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
            "education": resume.get("education", []),
            "projects": resume.get("projects", []),
            "experience": resume.get("experience", []),
            "certifications": resume.get("certifications", []),
            "ats_score": resume.get("ats_score", 70),
            "parsed_text": resume.get("parsed_text", "")
        }

        # Parse skills from JD if not explicitly provided
        required_skills = payload.required_skills
        if not required_skills:
            # Import parsing tools dynamically to parse JD description
            from services.parsing_engine import parse_skills
            required_skills = parse_skills(payload.job_description)
            if not required_skills:
                required_skills = ["React", "Python", "Docker", "SQL"]  # Default list

        job_details = {
            "job_title": payload.job_title,
            "required_skills": required_skills,
            "experience_level": payload.experience_level,
            "experience_years_required": payload.experience_years_required,
            "industry": payload.industry,
            "salary_range": payload.salary_range,
            "responsibilities": [line.strip() for line in payload.job_description.split("\n") if line.strip()][:5],
            "description": payload.job_description
        }

        # Run scoring engine for legacy metrics
        legacy_res = ScoringEngine.evaluate_job_match(resume_data, job_details)
        
        # Run SemanticMatchEngine for upgraded semantic fields
        from nlp.semantic_match_engine import SemanticMatchEngine
        semantic_res = await SemanticMatchEngine.match_resume_to_job(
            resume_data=resume_data,
            job_details=job_details,
            raw_text=resume_data.get("parsed_text", "")
        )
        
        match_res = {**legacy_res, **semantic_res}
        # align match_percentage with overall_score
        match_res["match_percentage"] = semantic_res["overall_score"]
        return match_res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Custom JD matching failed: {str(e)}"
        )

@router.get("/roadmap/{resume_id}/{job_title}")
async def get_role_roadmap(
    resume_id: str,
    job_title: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None or job_matches_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service offline."
        )

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume ID format."
        )

    try:
        resume = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume record not found."
            )

        resume_data = {
            "skills": resume.get("skills", []),
            "education": resume.get("education", []),
            "projects": resume.get("projects", []),
            "experience": resume.get("experience", []),
            "certifications": resume.get("certifications", []),
            "ats_score": resume.get("ats_score", 70)
        }

        # Look up missing skills for this job title from matching results
        match_doc = job_matches_collection.find_one({"resume_id": ObjectId(resume_id)})
        missing_skills = []
        if match_doc:
            for job in match_doc.get("recommended_jobs", []):
                if job.get("job_title", "").lower() == job_title.lower():
                    missing_skills = job.get("missing_skills", [])
                    break
        
        # Fallback if matching was never run or job wasn't matched
        if not missing_skills:
            # Let's infer missing skills based on a simulated requirements search
            jobs_list = JobMatcherCoordinator._load_job_dataset()
            for job in jobs_list:
                if job.get("job_title", "").lower() == job_title.lower():
                    # Calculate missing skills using standard SkillMatcher
                    skill_res = SkillMatcher.match_skills(resume_data["skills"], job["required_skills"])
                    missing_skills = skill_res["missing_skills"]
                    break

        roadmap = await JobRecommendationEngine.generate_learning_roadmap(
            job_title=job_title,
            missing_skills=missing_skills,
            resume_data=resume_data
        )

        return roadmap
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roadmap generation failed: {str(e)}"
        )
