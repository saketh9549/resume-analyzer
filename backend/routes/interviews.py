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
from database.mongodb import db, resumes_collection
from ai.response_parser import parse_ai_response

router = APIRouter()

interview_sessions_collection = db["interview_sessions"] if db is not None else None
api_key = os.getenv("GEMINI_API_KEY")

class StartInterviewRequest(BaseModel):
    resume_id: str
    job_title: str
    difficulty: Optional[str] = "Intermediate"

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

    questions = MOCK_QUESTIONS

    if api_key:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a Senior Technical Recruiter and Hiring Manager. Generate realistic technical, behavioral, and HR questions based on the candidate's resume and target job. Output in strict JSON format."
            )
            
            prompt = f"""
            Target Job Title: {payload.job_title}
            Difficulty Level: {payload.difficulty}
            Candidate Skills: {resume.get('skills', [])}
            Projects: {[{'name': p.get('name'), 'technologies': p.get('technologies')} for p in resume.get('projects', [])]}
            Experience: {[{'job_title': e.get('job_title'), 'duration': e.get('duration')} for e in resume.get('experience', [])]}
            
            Generate exactly 5 interview questions (mixture of technical, behavioral, and general HR) custom tailored for this candidate.
            Output matching this JSON schema:
            {{
              "questions": [
                {{
                  "question": "the interview question string",
                  "question_type": "technical | behavioral | hr",
                  "ideal_concepts": ["concept 1 key phrase", "concept 2 key phrase"]
                }}
              ]
            }}
            """
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            if response and response.text:
                parsed = parse_ai_response(response.text, {"questions": MOCK_QUESTIONS})
                questions = parsed.get("questions", MOCK_QUESTIONS)
        except Exception as e:
            logging.error(f"Gemini Interview generation failed: {e}. Using mock questions.")

    # Initialize session document
    session_questions = []
    for q in questions:
        session_questions.append({
            "question": q["question"],
            "question_type": q.get("question_type", "technical"),
            "ideal_concepts": q.get("ideal_concepts", []),
            "user_answer": "",
            "ai_evaluation": "",
            "score": None
        })

    session_doc = {
        "user_email": current_user["email"],
        "resume_id": ObjectId(payload.resume_id),
        "job_title": payload.job_title,
        "difficulty": payload.difficulty,
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
    
    # Defaults
    score = 75
    evaluation = "Good response. Try to highlight more quantitative details from your work projects."

    # Call Gemini for grading
    if api_key:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are an expert Interview Evaluator. Grade the user's answer against the interview question and list of ideal concepts. Output in strict JSON format."
            )
            
            prompt = f"""
            Question: "{target_q['question']}"
            Question Type: {target_q['question_type']}
            Ideal Concepts: {target_q['ideal_concepts']}
            User's Answer: "{payload.user_answer}"
            
            Provide a score (integer between 0 and 100) and constructive critique pointing out strengths and gaps in their answer.
            Output matching this JSON schema:
            {{
              "score": 85,
              "ai_evaluation": "Critique and improvements"
            }}
            """
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            if response and response.text:
                parsed = parse_ai_response(response.text, {"score": 75, "ai_evaluation": evaluation})
                score = parsed.get("score", score)
                evaluation = parsed.get("ai_evaluation", evaluation)
        except Exception as e:
            logging.error(f"Gemini grading failed: {e}")

    # Update question progress
    questions[payload.question_index]["user_answer"] = payload.user_answer
    questions[payload.question_index]["ai_evaluation"] = evaluation
    questions[payload.question_index]["score"] = int(score)

    interview_sessions_collection.update_one(
        {"_id": ObjectId(payload.session_id)},
        {"$set": {"questions": questions}}
    )

    return {
        "question_index": payload.question_index,
        "score": score,
        "ai_evaluation": evaluation
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
