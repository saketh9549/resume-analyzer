import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import google.generativeai as genai
from functools import partial

from services.auth_service import get_current_user
from database.mongodb import db, resumes_collection, users_collection
from ai.response_parser import parse_ai_response
from interviews.interview_context_builder import InterviewContextBuilder
from interviews.resume_question_generator import ResumeQuestionGenerator
from interviews.interview_ai_engine import InterviewAIEngine

router = APIRouter()

interview_sessions_collection = db["interview_sessions"] if db is not None else None
api_key = os.getenv("GEMINI_API_KEY")

class StartInterviewRequest(BaseModel):
    resume_id: str
    job_title: str
    difficulty: Optional[str] = "Intermediate"
    mode: Optional[str] = "Technical"

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_index: int
    user_answer: str

class CompleteInterviewRequest(BaseModel):
    session_id: str

# Mock fallbacks for offline testing
MOCK_QUESTIONS = [
    {"question": "How do you manage state transitions and coordinate REST endpoints under your Resume Analyzer stack?", "question_type": "technical", "ideal_concepts": ["FastAPI routers", "React Context", "local state"]},
    {"question": "Can you describe a challenging project experience and how you handled deadline constraints?", "question_type": "behavioral", "ideal_concepts": ["STAR method", "communication", "prioritization"]},
    {"question": "What is the difference between SQL indexing and MongoDB collections index rules?", "question_type": "technical", "ideal_concepts": ["B-Trees", "compilation times", "query performance"]},
    {"question": "Why do you want to transition into this target role?", "question_type": "hr", "ideal_concepts": ["motivation", "skills alignment", "growth"]},
    {"question": "How do you secure API routes to prevent unauthorized access?", "question_type": "technical", "ideal_concepts": ["JWT authentication", "HTTPS", "cors permissions"]}
]

@router.post("/start")
async def start_interview(
    payload: StartInterviewRequest,
    current_user: dict = Depends(get_current_user)
):
    if resumes_collection is None or interview_sessions_collection is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    resume = resumes_collection.find_one({
        "_id": ObjectId(payload.resume_id),
        "user_email": current_user["email"]
    })
    if not resume:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    try:
        # Build context
        context_data = InterviewContextBuilder.build_interview_context(payload.resume_id, current_user["email"])
        
        # Generate mode-specific questions
        questions = await ResumeQuestionGenerator.generate_questions(
            job_title=payload.job_title,
            difficulty=payload.difficulty,
            mode=payload.mode or "Technical",
            context_data=context_data
        )
    except Exception as e:
        logging.error(f"Failed to generate questions: {e}. Using mock fallbacks.")
        questions = MOCK_QUESTIONS

    # Initialize session document
    session_questions = []
    for q in questions:
        session_questions.append({
            "question": q["question"],
            "question_type": q.get("question_type", payload.mode or "technical"),
            "ideal_concepts": q.get("ideal_concepts", []),
            "user_answer": "",
            "ai_evaluation": "",
            "score": None,
            "confidence_score": None,
            "improvement_suggestions": "",
            "follow_up_question": ""
        })

    session_doc = {
        "user_email": current_user["email"],
        "resume_id": ObjectId(payload.resume_id),
        "job_title": payload.job_title,
        "difficulty": payload.difficulty,
        "mode": payload.mode or "Technical",
        "questions": session_questions,
        "readiness_score": None,
        "overall_feedback": "",
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = interview_sessions_collection.insert_one(session_doc)
    return {
        "session_id": str(result.inserted_id),
        "job_title": payload.job_title,
        "difficulty": payload.difficulty,
        "mode": payload.mode or "Technical",
        "questions": [{"index": i, "question": q["question"], "question_type": q["question_type"]} for i, q in enumerate(session_questions)]
    }

@router.post("/submit-answer")
async def submit_answer(
    payload: SubmitAnswerRequest,
    current_user: dict = Depends(get_current_user)
):
    if interview_sessions_collection is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    session = interview_sessions_collection.find_one({
        "_id": ObjectId(payload.session_id),
        "user_email": current_user["email"]
    })
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    if session["status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot edit completed interview sessions.")

    questions = session["questions"]
    if payload.question_index < 0 or payload.question_index >= len(questions):
        raise HTTPException(status_code=400, detail="Question index out of bounds.")

    target_q = questions[payload.question_index]
    
    # Run evaluation
    try:
        grade_res = await InterviewAIEngine.grade_answer(
            question=target_q["question"],
            question_type=target_q.get("question_type", "technical"),
            ideal_concepts=target_q.get("ideal_concepts", []),
            user_answer=payload.user_answer
        )
    except Exception as e:
        logging.error(f"Grading exception: {e}")
        grade_res = {
            "score": 70,
            "confidence_score": 65,
            "ai_evaluation": "Grading failed. Assuming average score.",
            "improvement_suggestions": "Try to expand on architectural trade-offs.",
            "follow_up_question": "Can you explain how you would scale this component?"
        }

    # Update question progress
    questions[payload.question_index]["user_answer"] = payload.user_answer
    questions[payload.question_index]["ai_evaluation"] = grade_res["ai_evaluation"]
    questions[payload.question_index]["score"] = int(grade_res["score"])
    questions[payload.question_index]["confidence_score"] = int(grade_res["confidence_score"])
    questions[payload.question_index]["improvement_suggestions"] = grade_res["improvement_suggestions"]
    questions[payload.question_index]["follow_up_question"] = grade_res["follow_up_question"]

    interview_sessions_collection.update_one(
        {"_id": ObjectId(payload.session_id)},
        {"$set": {"questions": questions}}
    )

    return {
        "question_index": payload.question_index,
        "score": grade_res["score"],
        "confidence_score": grade_res["confidence_score"],
        "ai_evaluation": grade_res["ai_evaluation"],
        "improvement_suggestions": grade_res["improvement_suggestions"],
        "follow_up_question": grade_res["follow_up_question"]
    }

@router.post("/complete")
async def complete_interview(
    payload: CompleteInterviewRequest,
    current_user: dict = Depends(get_current_user)
):
    if interview_sessions_collection is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    session = interview_sessions_collection.find_one({
        "_id": ObjectId(payload.session_id),
        "user_email": current_user["email"]
    })
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    questions = session["questions"]
    
    # Calculate average score of answered questions (questions with scores)
    scores = [q["score"] for q in questions if q["score"] is not None]
    readiness_score = int(sum(scores) / len(scores)) if scores else 0

    # Overall advice
    overall_feedback = "Great start. Focus on clarifying technical trade-offs during architectural questions."
    if readiness_score >= 85:
        overall_feedback = "Excellent preparedness. You demonstrate strong clarity, technical depth, and structure."
    elif readiness_score < 60:
        overall_feedback = "Additional practice is recommended. Focus on structure (STAR method) and review missing core technologies."

    interview_sessions_collection.update_one(
        {"_id": ObjectId(payload.session_id)},
        {"$set": {
            "status": "completed",
            "readiness_score": readiness_score,
            "overall_feedback": overall_feedback
        }}
    )

    # Sync: Write to User's interview_history and ai_feedback_history
    if users_collection is not None:
        try:
            users_collection.update_one(
                {"email": current_user["email"]},
                {
                    "$push": {
                        "interview_history": {
                            "session_id": str(session["_id"]),
                            "job_title": session.get("job_title"),
                            "difficulty": session.get("difficulty"),
                            "mode": session.get("mode", "Technical"),
                            "readiness_score": readiness_score,
                            "completed_at": datetime.now(timezone.utc).isoformat()
                        },
                        "ai_feedback_history": {
                            "topic": f"Interview Mode: {session.get('mode', 'Technical')} for {session.get('job_title')}",
                            "overall_feedback": overall_feedback,
                            "score": readiness_score,
                            "date": datetime.now(timezone.utc).isoformat()
                        }
                    }
                }
            )
        except Exception as e:
            logging.error(f"Failed to push user history: {e}")

    return {
        "session_id": payload.session_id,
        "readiness_score": readiness_score,
        "overall_feedback": overall_feedback,
        "status": "completed"
    }

@router.get("/history")
async def get_interview_history(
    current_user: dict = Depends(get_current_user)
):
    if interview_sessions_collection is None:
        return []

    try:
        cursor = interview_sessions_collection.find({"user_email": current_user["email"]}).sort("created_at", -1)
        results = []
        for doc in cursor:
            results.append({
                "id": str(doc["_id"]),
                "job_title": doc.get("job_title", ""),
                "difficulty": doc.get("difficulty", "Intermediate"),
                "readiness_score": doc.get("readiness_score"),
                "status": doc.get("status", "active"),
                "created_at": doc.get("created_at")[:10] if isinstance(doc.get("created_at"), str) else str(doc.get("created_at"))[:10]
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load interview history: {e}")
