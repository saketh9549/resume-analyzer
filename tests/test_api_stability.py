import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app

class TestAPIStability(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_resume_stats_precedence_without_auth(self):
        # Stats route should require auth and return 401, not 400 Bad Request (invalid ObjectId format)
        response = self.client.get("/resume/stats")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data.get("code"), 401)

    def test_resume_recent_precedence_without_auth(self):
        # Recent route should require auth and return 401, not 400 Bad Request
        response = self.client.get("/resume/recent")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data.get("code"), 401)

    def test_resume_analytics_precedence_without_auth(self):
        # Analytics route should require auth and return 401, not 400 Bad Request
        response = self.client.get("/resume/analytics")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data.get("code"), 401)

    def test_validation_exception_formatting(self):
        # Sending empty signup details should trigger validation exception handler
        response = self.client.post("/auth/signup", json={})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data.get("code"), 400)
        self.assertIn("Validation Error", data.get("error", ""))

    def test_recruiter_analytics_unauthorized(self):
        # Recruiter route should require auth and return 401
        response = self.client.get("/recruiter/analytics")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data.get("code"), 401)

if __name__ == "__main__":
    unittest.main()
