from pydantic import BaseModel
from typing import Optional

class UserSignup(BaseModel):

    name: str
    email: str
    password: str
    role: Optional[str] = "candidate"


class UserLogin(BaseModel):

    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str