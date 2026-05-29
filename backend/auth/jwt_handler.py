import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from config.settings import settings

SECRET_KEY = settings.JWT_SECRET
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
