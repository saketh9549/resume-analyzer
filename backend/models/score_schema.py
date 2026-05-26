from pydantic import Field
from typing import List
from models.common import MongoBaseModel, PyObjectId

class ResumeScoresSchema(MongoBaseModel):
    """
    Pydantic schema representing the 'resume_scores' collection in MongoDB.
    """
    resume_id: PyObjectId = Field(..., description="Reference ID to the associated resume")
    ats_score: int = Field(..., ge=0, le=100, description="Aggregated overall ATS match score (0-100)")
    skills_score: int = Field(..., ge=0, le=100, description="Skills breadth and match score (0-100)")
    experience_score: int = Field(..., ge=0, le=100, description="Work experience depth score (0-100)")
    formatting_score: int = Field(..., ge=0, le=100, description="Layout format, margins, and readability score (0-100)")
    missing_skills: List[str] = Field(default_factory=list, description="Identified critical missing technical skills")
    suggestions: List[str] = Field(default_factory=list, description="Actionable improvement suggestions for candidate")
