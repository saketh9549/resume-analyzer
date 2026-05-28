from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import logging
from datetime import datetime, timezone

from models.user_model import (
    UserSignup,
    UserLogin,
    ChangePasswordRequest
)
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user
)
from database.mongodb import db
from auth.security import validate_password_strength
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

    # Validate strength of the initial signup password
    validate_password_strength(user.password)

    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role or "candidate"
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
        "email": existing_user["email"],
        "role": existing_user.get("role", "candidate")
    })
    
    refresh_token = create_refresh_token({
        "email": existing_user["email"]
    })

    # Save to database
    from datetime import timedelta
    if db is not None:
        db["refresh_tokens"].insert_one({
            "email": existing_user["email"],
            "token": refresh_token,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        })

    return {
        "message": "Login successful",
        "access_token": token,
        "refresh_token": refresh_token,
        "user": {
            "name": existing_user["name"],
            "email": existing_user["email"],
            "role": existing_user.get("role", "candidate")
        }
    }

@router.put("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database offline."
        )

    # Fetch fresh user record
    user_in_db = users_collection.find_one({"email": current_user["email"]})
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found."
        )

    # Validate current password
    if not verify_password(payload.current_password, user_in_db["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password."
        )

    # Validate new password strength
    validate_password_strength(payload.new_password)

    # Hash new password
    hashed = hash_password(payload.new_password)

    # Update database
    users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": {"password": hashed}}
    )

    return {"message": "Password changed successfully"}


# Pydantic Request schemas for security flows
class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

class RequestVerificationRequest(BaseModel):
    email: str

class VerifyEmailRequest(BaseModel):
    email: str
    otp: str


@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest):
    if db is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    try:
        import jwt
        from auth.jwt_handler import SECRET_KEY
        token_payload = jwt.decode(payload.refresh_token, SECRET_KEY, algorithms=["HS256"])
        
        if token_payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type.")
            
        email = token_payload.get("email")
        # Check if refresh token is in DB
        stored = db["refresh_tokens"].find_one({"token": payload.refresh_token, "email": email})
        if not stored:
            raise HTTPException(status_code=401, detail="Refresh token has been revoked or is invalid.")
            
        # Delete old token (Rotating Refresh Token pattern)
        db["refresh_tokens"].delete_one({"_id": stored["_id"]})
        
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
            
        new_access = create_access_token({"email": email, "role": user.get("role", "candidate")})
        new_refresh = create_refresh_token({"email": email})
        
        # Save new refresh token
        from datetime import timedelta
        db["refresh_tokens"].insert_one({
            "email": email,
            "token": new_refresh,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        })
        
        return {
            "access_token": new_access,
            "refresh_token": new_refresh
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired.")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {e}")


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    if users_collection is None or db is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    user = users_collection.find_one({"email": payload.email})
    if not user:
        # Prevent user enumeration attacks by returning success always
        return {"message": "If the email is registered, a reset OTP has been sent."}

    # Generate a deterministic mock 6-digit OTP code for local testing
    import random
    otp_code = str(random.randint(100000, 999999))
    
    # Store in password_resets collection
    db["password_resets"].update_one(
        {"email": payload.email},
        {"$set": {
            "email": payload.email,
            "otp": otp_code,
            "created_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"[SECURITY MONITOR] Password Reset OTP Code generated for {payload.email}: {otp_code}")
    
    return {"message": "If the email is registered, a reset OTP has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    if users_collection is None or db is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    # Find the OTP code in resets cache
    record = db["password_resets"].find_one({"email": payload.email, "otp": payload.otp})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset OTP code.")

    # Validate OTP expiry (10-minute window)
    created_at = record.get("created_at", "")
    if created_at:
        try:
            from datetime import timedelta
            otp_time = datetime.fromisoformat(created_at)
            if datetime.now(timezone.utc) - otp_time > timedelta(minutes=10):
                db["password_resets"].delete_one({"_id": record["_id"]})
                raise HTTPException(status_code=400, detail="OTP code has expired. Please request a new one.")
        except (ValueError, TypeError):
            pass  # If timestamp is malformed, allow the reset to proceed

    # Remove verification record
    db["password_resets"].delete_one({"_id": record["_id"]})

    # Validate password strength
    validate_password_strength(payload.new_password)

    # Hash and update
    hashed = hash_password(payload.new_password)
    users_collection.update_one(
        {"email": payload.email},
        {"$set": {"password": hashed}}
    )

    return {"message": "Password reset completed successfully. Please login with your new credentials."}


@router.post("/request-email-verification")
def request_email_verification(payload: RequestVerificationRequest):
    if users_collection is None or db is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    user = users_collection.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    import random
    otp_code = str(random.randint(100000, 999999))

    db["email_verifications"].update_one(
        {"email": payload.email},
        {"$set": {
            "email": payload.email,
            "otp": otp_code,
            "created_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    logger = logging.getLogger(__name__)
    logger.info(f"[SECURITY MONITOR] Email Verification OTP Code generated for {payload.email}: {otp_code}")

    return {"message": "Verification code has been sent."}


@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest):
    if users_collection is None or db is None:
        raise HTTPException(status_code=503, detail="Database offline.")

    record = db["email_verifications"].find_one({"email": payload.email, "otp": payload.otp})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    # Validate OTP expiry (10-minute window)
    created_at = record.get("created_at", "")
    if created_at:
        try:
            from datetime import timedelta
            otp_time = datetime.fromisoformat(created_at)
            if datetime.now(timezone.utc) - otp_time > timedelta(minutes=10):
                db["email_verifications"].delete_one({"_id": record["_id"]})
                raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")
        except (ValueError, TypeError):
            pass  # If timestamp is malformed, allow verification to proceed

    # Delete verification record
    db["email_verifications"].delete_one({"_id": record["_id"]})

    # Update user verification flag
    users_collection.update_one(
        {"email": payload.email},
        {"$set": {"is_verified": True}}
    )

    return {"message": "Email verified successfully."}

from typing import List, Optional

class CareerPreferencesPayload(BaseModel):
    preferred_roles: Optional[List[str]] = []
    preferred_technologies: Optional[List[str]] = []
    experience_level: Optional[str] = ""
    preferred_industries: Optional[List[str]] = []
    expected_salary: Optional[str] = ""
    remote_preference: Optional[str] = ""
    location_preference: Optional[str] = ""

@router.get("/preferences")
def get_preferences(current_user: dict = Depends(get_current_user)):
    if users_collection is None:
        raise HTTPException(status_code=503, detail="Database offline.")
    
    user = users_collection.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    return user.get("career_preferences", {
        "preferred_roles": [],
        "preferred_technologies": [],
        "experience_level": "",
        "preferred_industries": [],
        "expected_salary": "",
        "remote_preference": "",
        "location_preference": ""
    })

@router.post("/preferences")
def save_preferences(payload: CareerPreferencesPayload, current_user: dict = Depends(get_current_user)):
    if users_collection is None:
        raise HTTPException(status_code=503, detail="Database offline.")
        
    pref_dict = payload.dict()
    users_collection.update_one(
        {"email": current_user["email"]},
        {
            "$set": {
                "career_preferences": pref_dict,
                "preferred_roles": payload.preferred_roles or [],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    return {"message": "Preferences saved successfully", "preferences": pref_dict}