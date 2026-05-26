import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
import urllib.request
import json

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

async def fetch_and_cache_jobs() -> list:
    """
    Fetches raw remote jobs from Remotive API and caches them in MongoDB.
    Serves from cache if updated within last 15 minutes.
    """
    if live_jobs_cache_collection is None:
        return MOCK_LIVE_JOBS

    # Check cache freshness
    try:
        cache_doc = live_jobs_cache_collection.find_one({"type": "remotive_cache"})
        if cache_doc:
            updated_at = datetime.fromisoformat(cache_doc["updated_at"])
            # If less than 15 minutes old, return cached data
            if datetime.now(timezone.utc) - updated_at < timedelta(minutes=15):
                return cache_doc.get("jobs", [])
    except Exception as e:
        logger.error(f"Error checking live jobs cache: {e}")

    # Fetch from Remotive API
    try:
        url = "https://remotive.com/api/remote-jobs?limit=50"
        # Set a 5-second timeout for the request to avoid blocking
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            jobs = []
            raw_jobs = data.get("jobs", [])
            for job in raw_jobs[:40]:  # limit to top 40 to avoid huge document sizes
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
        # Attempt to serve stale cache
        try:
            cache_doc = live_jobs_cache_collection.find_one({"type": "remotive_cache"})
            if cache_doc:
                return cache_doc.get("jobs", [])
        except:
            pass
        return MOCK_LIVE_JOBS

@router.get("/recommendations")
async def get_live_job_recommendations(
    skills: str = "",
    current_user: dict = Depends(get_current_user)
):
    try:
        all_jobs = await fetch_and_cache_jobs()
        if not all_jobs:
            return []

        # If no skills parameter, check user's last uploaded resume skills
        user_skills = []
        if not skills and resumes_collection is not None:
            last_resume = resumes_collection.find_one(
                {"user_email": current_user["email"]},
                sort=[("date", -1)]
            )
            if last_resume:
                user_skills = [s.lower() for s in last_resume.get("skills", [])]

        if skills:
            user_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]

        if not user_skills:
            # Return unfiltered top 15 jobs if no skills info
            return all_jobs[:15]

        # Rank jobs by keyword match on title/description
        matched_jobs = []
        for job in all_jobs:
            text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            matching_count = sum(1 for skill in user_skills if skill in text)
            if matching_count > 0:
                matched_jobs.append({
                    **job,
                    "matching_skills_count": matching_count
                })

        # Sort by matching count descending
        matched_jobs.sort(key=lambda x: x.get("matching_skills_count", 0), reverse=True)
        
        # Clean description HTML tags from output for clean SaaS UI render
        import re
        for job in matched_jobs:
            desc = job["description"]
            clean_desc = re.sub(r'<[^>]*>', ' ', desc)
            clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
            job["description"] = clean_desc[:250] + "..." if len(clean_desc) > 250 else clean_desc

        return matched_jobs[:15]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live jobs lookup failed: {str(e)}")
