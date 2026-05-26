from datetime import datetime
from enum import Enum
from pydantic import Field
from models.common import MongoBaseModel, PyObjectId

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ResumeSchema(MongoBaseModel):
    """
    Pydantic schema representing the 'resumes' collection in MongoDB.
    """
    user_id: PyObjectId = Field(..., description="Reference ID to the associated user")
    resume_name: str = Field(..., min_length=1, description="Name of the resume file")
    file_path: str = Field(..., min_length=1, description="Path or URL to the saved file location")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    processing_status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING, 
        description="Workflow state of parsing/scoring pipeline"
    )
