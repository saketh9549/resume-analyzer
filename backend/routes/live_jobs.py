import asyncio
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException

from services.auth_service import get_current_user
from database.mongodb import db, resumes_collection

router = APIRouter()

live_jobs_cache_collection = db["live_jobs_cache"] if db is not None else None
logger = logging.getLogger(__name__)

# Fallback jobs if API fails
MOCK_LIVE_JOBS = [
    {
        "id": "mock_1",
        "title": "Remote React Developer",
        "company_name": "SaaS Launchpad",
        "category": "software-development",
        "candidate_required_location": "Worldwide",
        "salary": "$90k - $120k",
        "url": "https://remotive.com",
        "description": "Develop modern user interfaces using React, Redux, and Tailwind CSS."
    },
    {
        "id": "mock_2",
        "title": "FastAPI Backend Engineer",
        "company_name": "CloudOps Inc",
        "category": "software-development",
        "candidate_required_location": "USA / Europe",
        "salary": "$110k - $140k",
        "url": "https://remotive.com",
        "description": "Construct scalable REST APIs, secure token auth middleware, and MongoDB aggregations."
    }
]

async def _fetch_jobs_from_remotive() -> list:
    """
    Fetches remote jobs from Remotive API in a thread executor to avoid
    blocking the FastAPI async event loop with synchronous urllib I/O.
    """
    import urllib.request
    import json

    def _blocking_request():
        url = "https://remotive.com/api/remote-jobs?limit=50"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            return json.loads(response.read().decode())

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, _blocking_request)

    jobs = []
    for job in data.get("jobs", [])[:40]:
        jobs.append({
            "id": str(job.get("id")),
            "title": job.get("title", ""),
            "company_name": job.get("company_name", ""),
            "category": job.get("category", ""),
            "candidate_required_location": job.get("candidate_required_location", "Remote"),
            "salary": job.get("salary", "N/A"),
            "url": job.get("url", "https://remotive.com"),
            "description": job.get("description", "")
        })
    return jobs


async def fetch_and_cache_jobs() -> list:
    """
    Fetches remote jobs from Remotive and caches in MongoDB.
    Serves from cache when updated within the last 30 minutes.
    Uses a thread executor for the HTTP fetch to avoid blocking the event loop.
    """
    CACHE_TTL_MINUTES = 30

    if live_jobs_cache_collection is None:
        return MOCK_LIVE_JOBS

    # Check cache freshness first (fast DB read)
    try:
        cache_doc = live_jobs_cache_collection.find_one(
            {"type": "remotive_cache"},
            {"updated_at": 1, "jobs": 1}  # projection — skip _id overhead
        )
        if cache_doc:
            updated_at = datetime.fromisoformat(cache_doc["updated_at"])
            if datetime.now(timezone.utc) - updated_at < timedelta(minutes=CACHE_TTL_MINUTES):
                return cache_doc.get("jobs", [])
    except Exception as e:
        logger.error(f"Error checking live jobs cache: {e}")

    # Fetch from Remotive API in thread executor (non-blocking)
    try:
        jobs = await _fetch_jobs_from_remotive()

        # Update cache document
        live_jobs_cache_collection.update_one(
            {"type": "remotive_cache"},
            {"$set": {
                "type": "remotive_cache",
                "jobs": jobs,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        return jobs
    except Exception as e:
        logger.error(f"Failed to fetch live Remotive jobs: {e}. Serving from stale cache.")
        # Serve stale cache on API failure
        try:
            cache_doc = live_jobs_cache_collection.find_one(
                {"type": "remotive_cache"},
                {"jobs": 1}
            )
            if cache_doc:
                return cache_doc.get("jobs", [])
        except Exception:
            pass
        return MOCK_LIVE_JOBS

@router.get("/recommendations")
async def get_live_job_recommendations(
    skills: str = "",
    resume_id: str = "",
    current_user: dict = Depends(get_current_user)
):
    try:
        from jobs.career_preference_engine import CareerPreferenceEngine
        from jobs.job_preference_matcher import JobPreferenceMatcher
        from bson import ObjectId

        preferences = CareerPreferenceEngine.get_preferences(current_user["email"])
        
        if resume_id:
            if not ObjectId.is_valid(resume_id):
                raise HTTPException(status_code=400, detail="Invalid resume ID format.")

        # Load user skills
        user_skills = []
        if resume_id and resumes_collection is not None:
            try:
                resume = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_email": current_user["email"]})
                if resume:
                    user_skills = resume.get("skills", [])
            except Exception:
                pass

        if not user_skills and resumes_collection is not None:
            # Fallback to most recent resume
            resume = resumes_collection.find_one(
                {"user_email": current_user["email"]},
                sort=[("upload_date", -1)]
            )
            if resume:
                user_skills = resume.get("skills", [])

        if skills:
            user_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]

        all_jobs = await fetch_and_cache_jobs()
        if not all_jobs:
            return []

        # Rank jobs by preference match
        matched_jobs = []
        for job in all_jobs:
            match_details = JobPreferenceMatcher.evaluate_preference_match(job, preferences, user_skills)
            matched_jobs.append({
                **job,
                "match_percentage": match_details["match_percentage"],
                "match_reasons": match_details["match_reasons"],
                "skill_gaps": match_details["skill_gaps"],
                "recommended_certifications": match_details["recommended_certifications"]
            })

        # Sort by match percentage descending
        matched_jobs.sort(key=lambda x: x.get("match_percentage", 0), reverse=True)
        
        # Clean description HTML tags from output for clean SaaS UI render
        import re
        for job in matched_jobs:
            desc = job.get("description", "")
            clean_desc = re.sub(r'<[^>]*>', ' ', desc)
            clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
            job["description"] = clean_desc[:250] + "..." if len(clean_desc) > 250 else clean_desc

        return matched_jobs[:15]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live jobs lookup failed: {str(e)}")
