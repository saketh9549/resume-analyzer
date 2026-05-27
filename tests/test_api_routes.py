import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from fastapi.testclient import TestClient
from main import app

class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

if __name__ == "__main__":
    unittest.main()
