from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from models.common import MongoBaseModel, PyObjectId

# Interview Prep schemas
class InterviewQA(BaseModel):
    question: str
    question_type: str = "technical" # technical | behavioral | hr
    ideal_concepts: List[str] = Field(default_factory=list)
    user_answer: Optional[str] = ""
    ai_evaluation: Optional[str] = ""
    score: Optional[int] = None # 0 to 100

class InterviewSessionSchema(MongoBaseModel):
    user_email: str
    resume_id: PyObjectId
    job_title: str
    difficulty: str = "Intermediate"
    questions: List[InterviewQA] = Field(default_factory=list)
    readiness_score: Optional[int] = None
    overall_feedback: Optional[str] = ""
    status: str = "active" # active | completed
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Recruiter Shortlist schemas
class RecruiterShortlistSchema(MongoBaseModel):
    recruiter_email: str
    name: str = "Hiring Pipeline"
    candidates: List[Dict[str, Any]] = Field(default_factory=list) # List of dict with resume_id, user_email, added_at, notes
    created_at: datetime = Field(default_factory=datetime.utcnow)

# AI Rewrite Logs schemas
class RewriteHistoryLog(BaseModel):
    section: str # summary | experience | projects
    original_text: str
    suggested_text: str
    applied: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RewriteHistorySchema(MongoBaseModel):
    resume_id: PyObjectId
    user_email: str
    logs: List[RewriteHistoryLog] = Field(default_factory=list)
