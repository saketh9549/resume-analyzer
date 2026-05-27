from fastapi import Depends, HTTPException, status
from middleware.auth_guard import require_auth

class RoleGuard:
    """
    FastAPI dependency guard enforcing specific access permissions based on role fields.
    """
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(require_auth)) -> dict:
        user_role = current_user.get("role", "candidate")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {self.allowed_roles}. Your role: {user_role}"
            )
        return current_user
