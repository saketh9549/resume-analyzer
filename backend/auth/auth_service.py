import jwt
from fastapi import Depends, HTTPException, status
from auth.jwt_handler import oauth2_scheme, SECRET_KEY
from database.mongodb import users_collection

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in."
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is invalid. Email is missing."
            )
        if users_collection is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is currently offline. Please try again later."
            )
        user = users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authenticated user no longer exists."
            )
        # Convert ObjectId to string to support standard JSON serialization
        user["_id"] = str(user["_id"])
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again."
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials token: {str(e)}"
        )
