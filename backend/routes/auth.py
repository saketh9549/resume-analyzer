from fastapi import APIRouter

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

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if existing_user:

        return {
            "error": "User already exists"
        }

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

    existing_user = users_collection.find_one({
        "email": user.email
    })

    if not existing_user:

        return {
            "error": "User not found"
        }

    password_correct = verify_password(
        user.password,
        existing_user["password"]
    )

    if not password_correct:

        return {
            "error": "Invalid password"
        }

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