from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    status
)
import shutil
import os
from datetime import datetime, timezone
from bson import ObjectId
from services.auth_service import get_current_user
from services.extraction_service import extract_text
from services.parsing_engine import parse_resume
from services.scoring_engine import calculate_ats_score
from database.mongodb import resumes_collection

router = APIRouter()

# Ensure uploads directory is present to avoid FileNotFoundError
os.makedirs("uploads", exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    file_path = f"uploads/{file.filename}"

    # Save local file copy
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # 1. Perform Text Extraction (PDF / DOCX / TXT)
    text = extract_text(file_path)

    # 2. Perform Heuristic Resume Parsing
    parsed_data = parse_resume(text)

    # 3. Perform ATS Scoring Calculation
    scoring = calculate_ats_score(parsed_data, text)

    # Persist in MongoDB
    resume_doc = {
        "user_email": current_user["email"],
        "filename": file.filename,
        "file_path": file_path,
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
        "date": datetime.now(timezone.utc).isoformat()
    }

    inserted_id = ""
    if resumes_collection is not None:
        try:
            result = resumes_collection.insert_one(resume_doc)
            inserted_id = str(result.inserted_id)
        except Exception as e:
            print(f"MongoDB save failed: {e}")
    else:
        print("MongoDB is offline; analysis was performed but could not be logged.")

    return {
        "message": "Resume uploaded and analyzed successfully",
        "id": inserted_id,
        "filename": file.filename,
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
            "optimization_recommendations": doc.get("optimization_recommendations", [])
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
            "suggestions": doc.get("suggestions", [])
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ATS breakdown: {str(e)}"
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

    try:
        # Find uploads by user email, sort by descending date
        cursor = resumes_collection.find({"user_email": current_user["email"]}).sort("date", -1).limit(10)
        results = []
        for doc in cursor:
            results.append({
                "id": str(doc["_id"]),
                "name": doc["filename"],
                "score": f"{doc.get('ats_score', 0)}%",
                "date": doc["date"][:10]  # Just YYYY-MM-DD
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
        user_resumes = list(resumes_collection.find({"user_email": current_user["email"]}))
        total_uploads = len(user_resumes)

        if total_uploads > 0:
            avg_score = int(sum(r.get("ats_score", 0) for r in user_resumes) / total_uploads)
            all_skills = set()
            for r in user_resumes:
                all_skills.update(r.get("skills", []))
            skills_found_count = len(all_skills)
        else:
            avg_score = 0
            skills_found_count = 0

        # Calculate logical matching jobs based on score (e.g. higher score = more matches)
        job_matches = max(1, int(avg_score / 10)) if total_uploads > 0 else 0

        return {
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

    try:
        # Fetch the last 7 uploads in ascending order to plot historical progress
        cursor = resumes_collection.find({"user_email": current_user["email"]}).sort("date", 1).limit(7)
        results = []

        for doc in cursor:
            day_label = doc["date"][:10]
            try:
                # Convert to short weekday name
                parsed_date = datetime.fromisoformat(doc["date"])
                day_label = parsed_date.strftime("%a")
            except:
                pass
            results.append({
                "name": f"{day_label} ({doc['filename']})",
                "score": doc.get("ats_score", 0)
            })

        # Return default list if the user has no history
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
