from fastapi import APIRouter, HTTPException, status

from models.user_model import (
    UserSignup,
    UserLogin
)
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)

from database.mongodb import users_collection

router = APIRouter()

@router.post("/signup")
def signup(user: UserSignup):
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently offline. Please try again later."
        )

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password)
    }

    users_collection.insert_one(user_data)

    return {
        "message": "User created successfully"
    }

@router.post("/login")
def login(user: UserLogin):
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently offline. Please try again later."
        )

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found."
        )

    password_correct = verify_password(
        user.password,
        existing_user["password"]
    )

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )

    token = create_access_token({
        "email": existing_user["email"]
    })

    return {
        "message": "Login successful",
        "access_token": token,
        "user": {
            "name": existing_user["name"],
            "email": existing_user["email"]
        }
    }