from datetime import datetime
from typing import Optional
from pydantic import Field
from models.common import MongoBaseModel

class UserSchema(MongoBaseModel):
    """
    Pydantic schema representing the 'users' collection in MongoDB.
    """
    name: str = Field(..., min_length=1, description="Full name of the user")
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Unique email address")
    password_hash: str = Field(..., description="Bcrypt hashed password")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when user was created")
    last_login: Optional[datetime] = Field(default=None, description="Timestamp of the last login session")
    is_active: bool = Field(default=True, description="Indicates if the user account is active")
