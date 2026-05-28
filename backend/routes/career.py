"""
Career Intelligence Router — Enterprise AI Career Advisory System
Provides AI-powered career roadmaps, skill gap analysis, salary benchmarks,
and growth trajectory recommendations based on resume data.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from datetime import datetime, timezone

from services.auth_service import get_current_user
from database.mongodb import resumes_collection, db

logger = logging.getLogger(__name__)

router = APIRouter()

# Optional career intelligence collection
career_intel_collection = db["career_intelligence"] if db is not None else None


class CareerGoalRequest(BaseModel):
    resume_id: str
    target_role: str
    target_industry: Optional[str] = "Software Engineering"
    years_to_goal: Optional[int] = 2
    current_salary: Optional[int] = None
    target_salary: Optional[int] = None


class CareerInsightQuery(BaseModel):
    query: str
    resume_id: Optional[str] = None


# ──────────────────────────────────────────────
# GET /career/roadmap/{resume_id}
# Returns AI-generated career roadmap for a role
# ──────────────────────────────────────────────
@router.get("/roadmap/{resume_id}")
async def get_career_roadmap(
    resume_id: str,
    target_role: str = "Software Engineer",
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a personalized career roadmap based on the resume's current skill profile.
    Uses Gemini AI to produce milestones, skill recommendations, and timelines.
    """
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID format.")

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        skills = doc.get("skills", [])
        missing_skills = doc.get("missing_skills", [])
        experience = doc.get("experience", [])
        ats_score = doc.get("ats_score", 0)

        # Check if cached roadmap exists
        if career_intel_collection is not None:
            cached = career_intel_collection.find_one({
                "resume_id": ObjectId(resume_id),
                "target_role": target_role,
                "type": "roadmap"
            })
            if cached:
                cached.pop("_id", None)
                cached.pop("resume_id", None)
                return {**cached, "cached": True}

        # Generate AI roadmap via Gemini
        from ai.gemini_service import GeminiAIService
        resume_data = {
            "skills": skills,
            "experience": experience,
            "ats_score": ats_score,
            "missing_skills": missing_skills,
            "filename": doc.get("filename", "")
        }

        roadmap = await GeminiAIService.generate_career_roadmap(
            resume_data=resume_data,
            target_role=target_role
        )

        # Persist to career intelligence collection
        roadmap_doc = {
            "resume_id": ObjectId(resume_id),
            "user_email": current_user["email"],
            "target_role": target_role,
            "type": "roadmap",
            "roadmap": roadmap,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        if career_intel_collection is not None:
            career_intel_collection.update_one(
                {"resume_id": ObjectId(resume_id), "target_role": target_role, "type": "roadmap"},
                {"$set": roadmap_doc},
                upsert=True
            )

        return {
            "resume_id": resume_id,
            "target_role": target_role,
            "roadmap": roadmap,
            "current_skills": skills,
            "skill_gaps": missing_skills,
            "ats_score": ats_score,
            "cached": False
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Career roadmap generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Career roadmap failed: {str(e)}")


# ──────────────────────────────────────────────────────
# GET /career/skill-gap/{resume_id}
# Returns skill gap analysis for a target role
# ──────────────────────────────────────────────────────
@router.get("/skill-gap/{resume_id}")
async def get_skill_gap_analysis(
    resume_id: str,
    target_role: str = "Software Engineer",
    current_user: dict = Depends(get_current_user)
):
    """
    Computes skill gap between current resume profile and market requirements for the target role.
    Returns priority learning recommendations and estimated time-to-competency.
    """
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID format.")

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        skills = set(s.lower() for s in doc.get("skills", []))

        # Role-to-skills market requirements mapping
        ROLE_SKILLS_MAP = {
            "software engineer": ["Python", "JavaScript", "Git", "SQL", "REST APIs", "Docker", "Linux"],
            "data scientist": ["Python", "NumPy", "Pandas", "Scikit-learn", "SQL", "Matplotlib", "Statistics", "Machine Learning"],
            "machine learning engineer": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLOps", "Docker", "Kubernetes", "Git"],
            "frontend developer": ["React", "JavaScript", "TypeScript", "CSS", "HTML", "Git", "REST APIs", "Webpack"],
            "backend developer": ["Python", "Node.js", "SQL", "NoSQL", "Docker", "REST APIs", "Git", "Linux"],
            "devops engineer": ["Docker", "Kubernetes", "CI/CD", "Linux", "Terraform", "AWS", "Git", "Ansible"],
            "cloud architect": ["AWS", "GCP", "Azure", "Terraform", "Kubernetes", "Docker", "Networking", "Security"],
            "product manager": ["Agile", "JIRA", "Roadmapping", "SQL", "Analytics", "Stakeholder Management", "User Research"],
        }

        role_key = target_role.lower()
        required_skills = []
        for key, skills_list in ROLE_SKILLS_MAP.items():
            if key in role_key or role_key in key:
                required_skills = skills_list
                break

        if not required_skills:
            # Generic software engineering if no match
            required_skills = ROLE_SKILLS_MAP["software engineer"]

        present_skills = [s for s in required_skills if s.lower() in skills]
        gap_skills = [s for s in required_skills if s.lower() not in skills]

        # Priority classification
        priority_gaps = gap_skills[:3]
        secondary_gaps = gap_skills[3:6]
        long_term_gaps = gap_skills[6:]

        gap_percentage = (len(gap_skills) / len(required_skills) * 100) if required_skills else 0
        readiness = 100 - gap_percentage

        return {
            "resume_id": resume_id,
            "target_role": target_role,
            "overall_readiness": round(readiness, 1),
            "skill_gap_percentage": round(gap_percentage, 1),
            "current_matching_skills": present_skills,
            "priority_skill_gaps": priority_gaps,
            "secondary_skill_gaps": secondary_gaps,
            "long_term_skill_gaps": long_term_gaps,
            "total_required": len(required_skills),
            "total_present": len(present_skills),
            "total_missing": len(gap_skills),
            "estimated_learning_months": max(1, len(gap_skills) * 2),
            "recommendation": (
                "You are highly competitive for this role." if readiness >= 80 else
                "You need focused upskilling in a few key areas." if readiness >= 60 else
                "Significant skill development needed. Consider a structured learning plan."
            )
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Skill gap analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {str(e)}")


# ─────────────────────────────────────────────────────────
# GET /career/market-insights
# Returns industry salary benchmarks & demand signals
# ─────────────────────────────────────────────────────────
@router.get("/market-insights")
async def get_market_insights(
    role: str = "Software Engineer",
    current_user: dict = Depends(get_current_user)
):
    """
    Returns curated market intelligence including salary ranges, hiring trends,
    most demanded skills, and top companies for the given role.
    """
    # Curated market data (can be replaced with live API integration)
    MARKET_DATA = {
        "software engineer": {
            "salary_range": {"min": 70000, "max": 160000, "median": 110000},
            "demand_level": "Very High",
            "growth_rate": "25%",
            "top_skills": ["Python", "JavaScript", "React", "Docker", "Kubernetes", "AWS"],
            "top_companies": ["Google", "Meta", "Amazon", "Microsoft", "Netflix", "Stripe"],
            "job_openings": "450,000+",
            "remote_friendly": True
        },
        "data scientist": {
            "salary_range": {"min": 80000, "max": 175000, "median": 122000},
            "demand_level": "High",
            "growth_rate": "36%",
            "top_skills": ["Python", "Machine Learning", "SQL", "TensorFlow", "Statistics"],
            "top_companies": ["DeepMind", "OpenAI", "Palantir", "Databricks", "Snowflake"],
            "job_openings": "180,000+",
            "remote_friendly": True
        },
        "machine learning engineer": {
            "salary_range": {"min": 100000, "max": 210000, "median": 155000},
            "demand_level": "Very High",
            "growth_rate": "40%",
            "top_skills": ["Python", "PyTorch", "TensorFlow", "Kubernetes", "MLOps"],
            "top_companies": ["OpenAI", "Google DeepMind", "Anthropic", "Meta AI", "HuggingFace"],
            "job_openings": "95,000+",
            "remote_friendly": True
        },
        "devops engineer": {
            "salary_range": {"min": 85000, "max": 165000, "median": 120000},
            "demand_level": "High",
            "growth_rate": "22%",
            "top_skills": ["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Linux"],
            "top_companies": ["HashiCorp", "AWS", "Cloudflare", "GitLab", "Datadog"],
            "job_openings": "125,000+",
            "remote_friendly": True
        },
        "frontend developer": {
            "salary_range": {"min": 65000, "max": 145000, "median": 98000},
            "demand_level": "High",
            "growth_rate": "16%",
            "top_skills": ["React", "TypeScript", "CSS", "Next.js", "Performance Optimization"],
            "top_companies": ["Figma", "Vercel", "Shopify", "Airbnb", "GitHub"],
            "job_openings": "220,000+",
            "remote_friendly": True
        }
    }

    role_key = role.lower()
    matched_data = None
    for key, data in MARKET_DATA.items():
        if key in role_key or role_key in key:
            matched_data = data
            break

    if not matched_data:
        matched_data = MARKET_DATA["software engineer"]

    return {
        "role": role,
        "market_data": matched_data,
        "last_updated": "2026-Q2",
        "data_source": "ResumeAI Market Intelligence Engine"
    }


# ─────────────────────────────────────────────────────────
# GET /career/growth-trajectory/{resume_id}
# Analyzes career progression from resume experience
# ─────────────────────────────────────────────────────────
@router.get("/growth-trajectory/{resume_id}")
async def get_growth_trajectory(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyzes the career growth trajectory from the resume's experience section.
    Returns seniority level, progression speed, and next logical career moves.
    """
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID format.")

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        skills = doc.get("skills", [])
        experience = doc.get("experience", [])
        education = doc.get("education", [])
        ats_score = doc.get("ats_score", 0)
        extracted_entities = doc.get("extracted_entities", {})

        # Estimate experience years from extracted entities
        years_exp = 0
        exp_years_list = extracted_entities.get("years_of_experience", [])
        if exp_years_list:
            for entry in exp_years_list:
                try:
                    years_exp = max(years_exp, int(entry.get("value", 0)))
                except (ValueError, TypeError):
                    pass

        # Determine seniority level
        if years_exp >= 8:
            seniority = "Principal / Staff Engineer"
            next_levels = ["Engineering Manager", "Director of Engineering", "CTO Track"]
        elif years_exp >= 5:
            seniority = "Senior Engineer"
            next_levels = ["Principal Engineer", "Engineering Manager", "Tech Lead"]
        elif years_exp >= 3:
            seniority = "Mid-Level Engineer"
            next_levels = ["Senior Engineer", "Tech Lead", "Specialist"]
        elif years_exp >= 1:
            seniority = "Junior Engineer"
            next_levels = ["Mid-Level Engineer", "Full-Stack Developer", "Specialist"]
        else:
            seniority = "Entry Level / Graduate"
            next_levels = ["Junior Engineer", "Associate Developer", "Trainee"]

        # Analyze skills for specialization signal
        ai_ml_skills = {"python", "tensorflow", "pytorch", "scikit-learn", "machine learning", "nlp", "deep learning"}
        cloud_skills = {"aws", "gcp", "azure", "kubernetes", "docker", "terraform"}
        web_skills = {"react", "angular", "vue", "javascript", "typescript", "node.js"}

        skills_lower = set(s.lower() for s in skills)
        specialization = "Generalist"
        if len(skills_lower & ai_ml_skills) >= 3:
            specialization = "AI/ML Specialist"
        elif len(skills_lower & cloud_skills) >= 3:
            specialization = "Cloud/Infrastructure Specialist"
        elif len(skills_lower & web_skills) >= 3:
            specialization = "Web/Frontend Specialist"

        return {
            "resume_id": resume_id,
            "estimated_experience_years": years_exp,
            "seniority_level": seniority,
            "specialization": specialization,
            "next_career_levels": next_levels,
            "skills_count": len(skills),
            "experience_entries": len(experience),
            "education_entries": len(education),
            "ats_score": ats_score,
            "trajectory_score": min(100, ats_score + (years_exp * 5)),
            "growth_velocity": (
                "Accelerated" if ats_score >= 75 and years_exp >= 3 else
                "Steady" if ats_score >= 55 else
                "Early Stage"
            )
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Growth trajectory analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trajectory analysis failed: {str(e)}")


# ─────────────────────────────────────────────────────────
# GET /career/intelligence/summary/{resume_id}
# Returns unified career intelligence report
# ─────────────────────────────────────────────────────────
@router.get("/intelligence/summary/{resume_id}")
async def get_career_intelligence_summary(
    resume_id: str,
    target_role: str = "Software Engineer",
    current_user: dict = Depends(get_current_user)
):
    """
    Aggregates skill gap, market insights, and growth trajectory into a single
    career intelligence report for the given resume and target role.
    """
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID format.")

    try:
        # Directly call internal endpoint functions
        skill_gap = await get_skill_gap_analysis(resume_id, target_role, current_user)
        market_data = await get_market_insights(target_role, current_user)
        trajectory = await get_growth_trajectory(resume_id, current_user)

        return {
            "resume_id": resume_id,
            "target_role": target_role,
            "skill_gap_analysis": skill_gap,
            "market_intelligence": market_data,
            "growth_trajectory": trajectory,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Career intelligence summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")
