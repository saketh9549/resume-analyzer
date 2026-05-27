import sys
import os
import unittest
import warnings

# Suppress FutureWarnings and ResourceWarnings
warnings.simplefilter("ignore", category=FutureWarning)
warnings.simplefilter("ignore", category=ResourceWarning)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# pyrefly: ignore [missing-import]
from auth.password_utils import hash_password, verify_password
# pyrefly: ignore [missing-import]
from auth.security import validate_password_strength
# pyrefly: ignore [missing-import]
from auth.jwt_handler import create_access_token
from fastapi.exceptions import HTTPException

class TestAuthenticationSecurity(unittest.TestCase):
    def test_password_hashing_consistency(self):
        # Hash a password and verify it works
        pwd = "SecurePassword123"
        hashed = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("wrong_password", hashed))

    def test_password_strength_validation(self):
        # Strong password should pass
        try:
            validate_password_strength("validpassword")
        except HTTPException:
            self.fail("validate_password_strength raised HTTPException unexpectedly!")

        # Short password should fail
        with self.assertRaises(HTTPException) as ctx:
            validate_password_strength("12345")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("at least 6 characters", ctx.exception.detail)

    def test_jwt_token_generation(self):
        payload = {"email": "tester@test.com"}
        token = create_access_token(payload)
        self.assertTrue(isinstance(token, str))
        self.assertTrue(len(token) > 0)

if __name__ == '__main__':
    unittest.main()
