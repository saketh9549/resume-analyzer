import os
import logging
import asyncio
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import google.generativeai as genai
from functools import partial

from services.auth_service import get_current_user
from database.mongodb import db, resumes_collection
from ai.response_parser import parse_ai_response
from config.settings import settings

router = APIRouter()

rewrite_history_collection = db["rewrite_history"] if db is not None else None
api_key = settings.GEMINI_API_KEY

class RewriteRequest(BaseModel):
    resume_id: str
    section: str # summary | experience | projects
    original_text: str
    focus_area: Optional[str] = "ATS Optimization"

REWRITE_FALLBACK = {
    "suggested_text": "Experienced engineering specialist with verified record building fast backends and clean user screens. Reduced system latencies by 30% by refactoring DB indices and automating container releases.",
    "key_improvements": [
        "Replaced descriptive terms with action-driven technical metrics.",
        "Highlighted quantitative outcomes rather than passive tasks."
    ]
}

@router.post("/rewrite")
async def rewrite_resume_section(
    payload: RewriteRequest,
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

    # 1. Verify resume access
    resume = resumes_collection.find_one({
        "_id": ObjectId(payload.resume_id),
        "user_email": current_user["email"]
    })
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied."
        )

    suggested_text = REWRITE_FALLBACK["suggested_text"]
    key_improvements = REWRITE_FALLBACK["key_improvements"]

    # 2. Call Gemini API if available
    if api_key:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a Professional Resume Writer and Technical Recruiter. Your task is to rewrite a resume section to maximize ATS impact and recruiter readability. Output in strict JSON format."
            )
            
            prompt = f"""
            Target Section: {payload.section}
            Original Text: "{payload.original_text}"
            Focus Area: {payload.focus_area}
            
            Rewrite this content to be highly engaging, leading with action verbs and inserting quantitative impact where possible.
            Provide output matching this JSON schema:
            {{
              "suggested_text": "the rewritten resume text",
              "key_improvements": ["improvement 1 description", "improvement 2 description"]
            }}
            """
            
            loop = asyncio.get_running_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                parsed = parse_ai_response(response.text, REWRITE_FALLBACK)
                suggested_text = parsed.get("suggested_text", suggested_text)
                key_improvements = parsed.get("key_improvements", key_improvements)
        except Exception as e:
            logging.error(f"Gemini Section Rewrite API failed: {e}")

    # 3. Log to Rewrite History
    if rewrite_history_collection is not None:
        try:
            log_entry = {
                "section": payload.section,
                "original_text": payload.original_text,
                "suggested_text": suggested_text,
                "applied": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            rewrite_history_collection.update_one(
                {
                    "resume_id": ObjectId(payload.resume_id),
                    "user_email": current_user["email"]
                },
                {
                    "$push": {"logs": log_entry}
                },
                upsert=True
            )
        except Exception as e:
            logging.error(f"Failed to log rewrite history: {e}")

    return {
        "original_text": payload.original_text,
        "suggested_text": suggested_text,
        "key_improvements": key_improvements
    }
