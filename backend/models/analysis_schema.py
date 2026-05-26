from datetime import datetime
from typing import List, Optional
from pydantic import Field, BaseModel
from models.common import MongoBaseModel, PyObjectId

class EducationDetail(BaseModel):
    institution: str = Field(..., description="Name of university or school")
    degree: str = Field(..., description="Field of study or degree received")
    year: Optional[int] = Field(default=None, description="Graduation year")

class ProjectDetail(BaseModel):
    title: str = Field(..., description="Title of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies used in project")

class ExperienceDetail(BaseModel):
    company: str = Field(..., description="Name of company or employer")
    role: str = Field(..., description="Designation or job title")
    duration: Optional[str] = Field(default=None, description="Duration of employment (e.g. '1 Year')")

class ResumeAnalysisSchema(MongoBaseModel):
    """
    Pydantic schema representing the 'resume_analysis' collection in MongoDB.
    """
    resume_id: PyObjectId = Field(..., description="Reference ID to the associated resume")
    parsed_text: str = Field(..., description="Unstructured raw text content parsed from the resume file")
    education: List[EducationDetail] = Field(default_factory=list, description="Parsed academic history entries")
    projects: List[ProjectDetail] = Field(default_factory=list, description="Parsed project highlight entries")
    experience: List[ExperienceDetail] = Field(default_factory=list, description="Parsed professional job entries")
    certifications: List[str] = Field(default_factory=list, description="List of parsed certifications and awards")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis creation timestamp")
