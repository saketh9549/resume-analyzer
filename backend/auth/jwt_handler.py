import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET", "resume_analyzer_secret_key_secure_32_bytes")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    # Use timezone-aware UTC datetime for expiration
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=1)
    payload["type"] = "access"
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )
    return token

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    # Expire in 7 days
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
    payload["type"] = "refresh"
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )
    return token
