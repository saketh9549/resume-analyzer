from typing import Optional
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException, status
from models.user_schema import UserSchema
from repositories.base_repository import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase

class UserRepository(BaseRepository[UserSchema]):
    """
    Data access layer for the 'users' collection.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users", UserSchema)

    async def get_by_email(self, email: str) -> Optional[UserSchema]:
        """
        Queries a single user from the database matching the unique email address parameter.
        """
        doc = await self.collection.find_one({"email": email.strip().lower()})
        if doc:
            return self.model_class.model_validate(doc)
        return None

    async def create_user(self, user: UserSchema) -> UserSchema:
        """
        Saves a user record while trapping DuplicateKeyError indexes errors gracefully.
        """
        # Ensure email format is normalized prior to DB checks
        user.email = user.email.strip().lower()
        try:
            return await self.create(user)
        except DuplicateKeyError:
            # Trap email index conflict scenarios and raise detailed client exception
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration conflict: The email address '{user.email}' is already registered."
            )
