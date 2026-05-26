from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import Field, BaseModel
from models.common import MongoBaseModel, PyObjectId

class JobMatchDetail(BaseModel):
    job_title: str
    match_percentage: int
    readiness_level: str
    skills_score: int
    experience_score: int
    project_score: int
    education_score: int
    certs_score: int
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)
    candidate_exp_years: float = 0.0
    required_exp_years: int = 0

class CareerGuidanceDetail(BaseModel):
    career_summary: str = ""
    recommended_tracks: List[Dict[str, Any]] = Field(default_factory=list)
    overall_guidance: str = ""
    transition_advice: str = ""

class JobMatchSchema(MongoBaseModel):
    """
    Pydantic schema representing the 'job_matches' collection in MongoDB.
    """
    resume_id: PyObjectId = Field(..., description="Reference ID to the associated resume record")
    user_email: str = Field(..., description="Owner's user email identifier")
    user_id: Optional[PyObjectId] = Field(None, description="Optional reference ID to user ID")
    recommended_jobs: List[JobMatchDetail] = Field(default_factory=list, description="Top evaluated job fits")
    career_guidance: CareerGuidanceDetail = Field(default_factory=CareerGuidanceDetail, description="AI Career coach recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Evaluation run date")
