from typing import Optional, Any
from bson import ObjectId
from models.score_schema import ResumeScoresSchema
from repositories.base_repository import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase

class ResumeScoresRepository(BaseRepository[ResumeScoresSchema]):
    """
    Data access layer for the 'resume_scores' collection.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "resume_scores", ResumeScoresSchema)

    async def get_by_resume_id(self, resume_id: Any) -> Optional[ResumeScoresSchema]:
        """
        Retrieves the grading score breakdown document associated with a specific resume.
        """
        if isinstance(resume_id, str) and ObjectId.is_valid(resume_id):
            resume_id = ObjectId(resume_id)
        results = await self.get_all({"resume_id": resume_id})
        return results[0] if results else None
