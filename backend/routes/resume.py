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

from fastapi.responses import FileResponse
from pydantic import BaseModel
from multimodal.multimodal_service import MultimodalService

class RenameRequest(BaseModel):
    name: str

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        # Delete physical file on disk
        file_path = doc.get("file_path", "")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as fe:
                print(f"Failed to delete physical file: {fe}")

        # Delete document from resumes collection
        resumes_collection.delete_one({"_id": ObjectId(resume_id)})

        # Cascaded cleanups of linked collections to prevent DB bloat
        from database.mongodb import db
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
async def rename_resume(
    resume_id: str,
    payload: RenameRequest,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        # Update filename in MongoDB
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {"filename": payload.name}}
        )

        return {"message": "Resume renamed successfully", "name": payload.name}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")

@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        file_path = doc.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Physical file does not exist on server.")

        return FileResponse(
            path=file_path,
            filename=doc.get("filename", "resume.pdf"),
            media_type="application/pdf"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.post("/{resume_id}/reanalyze")
async def reanalyze_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None:
        raise HTTPException(status_code=503, detail="Database service offline.")

    try:
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id),
            "user_email": current_user["email"]
        })
        if not doc:
            raise HTTPException(status_code=404, detail="Resume record not found.")

        file_path = doc.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Physical file missing.")

        # Re-run extraction, parsing, and scoring pipeline
        text = extract_text(file_path)
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
                "date": datetime.now(timezone.utc).isoformat()
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

@router.post("/{resume_id}/multimodal-analyze")
async def multimodal_analyze(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await MultimodalService.analyze_resume_visuals(resume_id, current_user["email"])
        return result
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multimodal vision audit failed: {str(e)}")

