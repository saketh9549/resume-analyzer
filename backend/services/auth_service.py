# backend/services/auth_service.py
# Re-exposes new centralized auth components to maintain full backward-compatibility

from auth.jwt_handler import SECRET_KEY, oauth2_scheme, create_access_token, create_refresh_token
from auth.password_utils import hash_password, verify_password
from auth.auth_service import get_current_user