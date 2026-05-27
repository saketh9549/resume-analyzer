from fastapi import HTTPException, status

def validate_password_strength(password: str):
    """
    Validates that password matches minimum security criteria:
    - Minimum length: 6 characters
    """
    if not password or len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )
