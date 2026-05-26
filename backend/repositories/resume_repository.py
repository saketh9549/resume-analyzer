from typing import List, Any
from bson import ObjectId
from models.resume_schema import ResumeSchema, ProcessingStatus
from repositories.base_repository import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase

class ResumeRepository(BaseRepository[ResumeSchema]):
    """
    Data access layer for the 'resumes' collection.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "resumes", ResumeSchema)

    async def get_by_user_id(self, user_id: Any) -> List[ResumeSchema]:
        """
        Queries all resume documents submitted by a specific user.
        """
        if isinstance(user_id, str) and ObjectId.is_valid(user_id):
            user_id = ObjectId(user_id)
        return await self.get_all({"user_id": user_id})

    async def update_status(self, resume_id: Any, status: ProcessingStatus) -> bool:
        """
        Updates the processing pipeline state flags for a specific resume record.
        """
        if isinstance(resume_id, str) and ObjectId.is_valid(resume_id):
            resume_id = ObjectId(resume_id)
        return await self.update(resume_id, {"processing_status": status})
