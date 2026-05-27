from fastapi import Depends, HTTPException, status
from services.auth_service import get_current_user

def require_auth(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to assert that the request user is authenticated and active.
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )
    # Expose user ID back in standard format if present
    if "_id" in current_user and "id" not in current_user:
        current_user["id"] = str(current_user["_id"])
    return current_user
