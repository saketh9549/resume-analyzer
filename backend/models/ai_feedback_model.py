from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import Field, BaseModel
from models.common import MongoBaseModel, PyObjectId

class AIFeedbackDetail(BaseModel):
    """
    Structured feedback details returned by Gemini.
    """
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    missing_technologies: List[str] = Field(default_factory=list)
    career_readiness: str = Field(default="Intermediate")
    recruiter_feedback: str = Field(default="")
    project_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    experience_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    learning_recommendations: List[str] = Field(default_factory=list)

class AIFeedbackSchema(MongoBaseModel):
    """
    Pydantic schema representing the 'ai_feedback' collection in MongoDB.
    """
    resume_id: PyObjectId = Field(..., description="Reference ID to the associated resume record")
    user_id: PyObjectId = Field(..., description="Reference ID to the associated user account")
    ai_feedback: AIFeedbackDetail = Field(..., description="Structured AI findings")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Feedback generation date")
