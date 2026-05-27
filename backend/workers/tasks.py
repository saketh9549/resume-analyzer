import asyncio
import logging
import os
import tempfile
from bson import ObjectId
from datetime import datetime, timezone

from workers.celery_worker import celery_app
from database.mongodb import resumes_collection, db
from services.extraction_service import extract_text
from services.parsing_engine import parse_resume
from services.scoring_engine import calculate_ats_score
from embeddings.embedding_service import EmbeddingService
from ai.gemini_service import GeminiAIService
from storage.gridfs_service import GridFSService
from multimodal.multimodal_service import MultimodalService
from workers.redis_config import publish_event

logger = logging.getLogger(__name__)
ai_feedback_collection = db["ai_feedback"] if db is not None else None

@celery_app.task
def process_resume_parsing_task(file_path: str, user_email: str, filename: str) -> str:
    """
    Background worker task to extract text, parse section data, 
    and calculate initial ATS scores for uploaded documents.
    """
    logger.info(f"Starting background parse task for file: {filename}")
    try:
        # 1. Perform Text Extraction
        text = extract_text(file_path)

        # 2. Perform Heuristic Resume Parsing
        parsed_data = parse_resume(text)

        # 3. Perform ATS Scoring Calculation
        scoring = calculate_ats_score(parsed_data, text)

        # 4. Compile DB document
        resume_doc = {
            "user_email": user_email,
            "filename": filename,
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

        if resumes_collection is not None:
            result = resumes_collection.insert_one(resume_doc)
            resume_id = str(result.inserted_id)
            
            # Immediately trigger secondary embedding extraction in background
            generate_embeddings_task.delay(resume_id)
            return resume_id
            
        return "Database Offline"
    except Exception as e:
        logger.error(f"Failed parsing background task: {e}")
        raise e

@celery_app.task
def generate_embeddings_task(resume_id_str: str):
    """
    Asynchronously generates and caches text embeddings for the parsed resume.
    """
    logger.info(f"Generating semantic embeddings for resume: {resume_id_str}")
    if resumes_collection is None:
        return "Offline"

    try:
        doc = resumes_collection.find_one({"_id": ObjectId(resume_id_str)})
        if not doc:
            logger.error("Resume record not found for embedding task.")
            return "Not Found"

        # Combine parsed text + found skills for robust semantic context
        text_context = doc.get("parsed_text", "")
        skills_context = " ".join(doc.get("skills", []))
        combined_payload = f"{doc.get('filename', '')} {skills_context} {text_context}"

        # Execute async embedding generation synchronously inside worker task
        async def run_embedding():
            await EmbeddingService.get_embedding(combined_payload)
            
        asyncio.run(run_embedding())
        logger.info(f"Embeddings generated and cached successfully for {resume_id_str}")
        return "Completed"
    except Exception as e:
        logger.error(f"Failed to generate embeddings in background worker: {e}")
        raise e

@celery_app.task
def generate_ai_feedback_task(resume_id_str: str, user_id_str: str, model_name: str, strictness: str):
    """
    Asynchronously triggers Gemini AI review generator and upserts standard collections.
    """
    logger.info(f"Generating background AI feedback for: {resume_id_str}")
    if resumes_collection is None or ai_feedback_collection is None:
        return "Offline"

    try:
        resume = resumes_collection.find_one({"_id": ObjectId(resume_id_str)})
        if not resume:
            return "Resume Not Found"

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

        async def run_feedback():
            ai_result = await GeminiAIService.analyze_resume(
                resume_data=resume_data,
                model_name=model_name,
                strictness=strictness
            )
            
            feedback_doc = {
                "resume_id": ObjectId(resume_id_str),
                "user_id": ObjectId(user_id_str) if user_id_str else None,
                "ai_feedback": {
                    "strengths": ai_result.get("strengths", []),
                    "weaknesses": ai_result.get("weaknesses", []),
                    "suggestions": ai_result.get("suggestions", []),
                    "recruiter_feedback": ai_result.get("recruiter_feedback", ""),
                    "career_readiness": ai_result.get("career_readiness", "Intermediate")
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            ai_feedback_collection.update_one(
                {"resume_id": ObjectId(resume_id_str)},
                {"$set": feedback_doc},
                upsert=True
            )

        asyncio.run(run_feedback())
        logger.info(f"AI feedback completed in background for {resume_id_str}")
        return "Completed"
    except Exception as e:
        logger.error(f"AI feedback task failed: {e}")
        raise e


def update_status(resume_id: str, status: str, progress: int, message: str):
    """
    Helper function to update DB status and publish WebSockets updates via Redis PubSub
    """
    logger.info(f"Resume {resume_id} state transition: {status} ({progress}%) - {message}")
    if resumes_collection is not None:
        try:
            resumes_collection.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": {"analysis_status": status, "progress": progress, "progress_message": message}}
            )
        except Exception as db_err:
            logger.error(f"Failed to update MongoDB resume state: {db_err}")
    publish_event(f"analysis_channel_{resume_id}", {
        "status": status,
        "progress": progress,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@celery_app.task(name="workers.tasks.run_async_analysis_task")
def run_async_analysis_task(resume_id_str: str, user_email: str) -> str:
    logger.info(f"Starting unified async analysis task for resume: {resume_id_str}")
    update_status(resume_id_str, "queued", 5, "Resume analysis task queued in background.")

    if resumes_collection is None:
        update_status(resume_id_str, "failed", 0, "Database connection is offline.")
        return "Offline"

    try:
        # 1. Fetch document
        doc = resumes_collection.find_one({
            "_id": ObjectId(resume_id_str),
            "user_email": user_email
        })
        if not doc:
            update_status(resume_id_str, "failed", 0, "Resume document not found.")
            return "Not Found"

        # 2. Extract Text
        update_status(resume_id_str, "extracting", 15, "Extracting text from document...")
        
        gridfs_file_id = doc.get("gridfs_file_id")
        file_path = doc.get("file_path", "")
        temp_file_path = None

        if gridfs_file_id:
            try:
                file_bytes = GridFSService.read_file(ObjectId(gridfs_file_id))
                suffix = os.path.splitext(doc.get("filename", ".pdf"))[1].lower()
                temp_file_fd, temp_file_path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(temp_file_fd, 'wb') as temp_file:
                    temp_file.write(file_bytes)
                file_path = temp_file_path
            except Exception as e:
                logger.error(f"Failed to fetch file from GridFS in celery: {e}")

        if not file_path or not os.path.exists(file_path):
            update_status(resume_id_str, "failed", 0, "Source document file not found.")
            return "File Missing"

        try:
            text = extract_text(file_path)
        except Exception as e:
            update_status(resume_id_str, "failed", 0, f"Extraction failed: {str(e)}")
            return "Extraction Failed"
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    logger.error(f"Failed to delete temp file in task: {e}")

        # 3. Parse & Run Heuristics
        update_status(resume_id_str, "analyzing", 35, "Parsing section content and extracting skills...")
        parsed_data = parse_resume(text)
        
        # 4. ATS Scoring
        update_status(resume_id_str, "analyzing", 50, "Evaluating ATS score and optimization recommendations...")
        scoring = calculate_ats_score(parsed_data, text)

        # Update resumes_collection with parsing & ATS results
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id_str)},
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

        # 5. Embedding Generation
        update_status(resume_id_str, "embedding", 70, "Generating text embeddings for semantic matching...")
        skills_context = " ".join(parsed_data["skills"])
        combined_payload = f"{doc.get('filename', '')} {skills_context} {text}"
        
        async def run_embedding():
            from vector_db.semantic_search import add_resume_vector
            await add_resume_vector(
                resume_id_str=resume_id_str,
                text=combined_payload,
                filename=doc.get("filename", ""),
                user_email=user_email
            )
        asyncio.run(run_embedding())

        # 6. AI Recruiter Coaching Review
        update_status(resume_id_str, "matching", 85, "Running AI recruiter coaching review...")
        
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

        async def run_feedback():
            ai_result = await GeminiAIService.analyze_resume(
                resume_data=resume_data,
                model_name="gemini-2.5-flash",
                strictness="standard"
            )
            feedback_doc = {
                "resume_id": ObjectId(resume_id_str),
                "user_id": doc.get("user_id") or None,
                "ai_feedback": {
                    "strengths": ai_result.get("strengths", []),
                    "weaknesses": ai_result.get("weaknesses", []),
                    "suggestions": ai_result.get("suggestions", []),
                    "recruiter_feedback": ai_result.get("recruiter_feedback", ""),
                    "career_readiness": ai_result.get("career_readiness", "Intermediate")
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            if ai_feedback_collection is not None:
                ai_feedback_collection.update_one(
                    {"resume_id": ObjectId(resume_id_str)},
                    {"$set": feedback_doc},
                    upsert=True
                )
        asyncio.run(run_feedback())

        # 7. Multimodal Scan (if PDF)
        if doc.get("filename", "").lower().endswith(".pdf"):
            update_status(resume_id_str, "matching", 92, "Running Gemini Vision layout audit...")
            try:
                async def run_multimodal():
                    await MultimodalService.analyze_resume_visuals(resume_id_str, user_email)
                asyncio.run(run_multimodal())
            except Exception as me:
                logger.error(f"Multimodal vision scan failed in task: {me}")

        # 8. Complete!
        update_status(resume_id_str, "completed", 100, "Resume analysis completed successfully.")
        return "Success"

    except Exception as e:
        logger.error(f"General failure inside async celery task: {e}")
        update_status(resume_id_str, "failed", 0, f"Analysis failed: {str(e)}")
        raise e
