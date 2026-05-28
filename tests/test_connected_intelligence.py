import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from fastapi.testclient import TestClient
from main import app
from services.auth_service import get_current_user

class TestConnectedIntelligence(unittest.TestCase):
    def setUp(self):
        # Override authentication dependency to return test user
        self.mock_user = {
            "id": "60d0fe4f5311236168e109ca",
            "email": "test@example.com",
            "name": "Test User",
            "role": "candidate"
        }
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        self.client = TestClient(app)

    def tearDown(self):
        # Reset dependency overrides
        app.dependency_overrides.clear()

    @patch("routes.resume.resumes_collection")
    def test_get_user_resumes(self, mock_resumes_collection):
        # Mock database cursor for resumes collection
        mock_cursor = [
            {
                "_id": ObjectId("60d0fe4f5311236168e109cb"),
                "filename": "resume1.pdf",
                "ats_score": 85,
                "upload_date": "2026-05-28T00:00:00Z",
                "category": "software-development",
                "analysis_status": "analyzed"
            }
        ]
        mock_resumes_collection.find.return_value.sort.return_value = mock_cursor

        response = self.client.get("/resumes/user")
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertEqual(len(res_data), 1)
        self.assertEqual(res_data[0]["name"], "resume1.pdf")
        self.assertEqual(res_data[0]["score"], "85%")

    @patch("routes.resume.resumes_collection")
    def test_get_resume_by_id(self, mock_resumes_collection):
        resume_id = "60d0fe4f5311236168e109cb"
        mock_resume = {
            "_id": ObjectId(resume_id),
            "filename": "resume1.pdf",
            "skills": ["React", "FastAPI"],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "contact": {},
            "ats_score": 85,
            "category_scores": {},
            "missing_skills": ["Docker"],
            "suggestions": [],
            "detected_strengths": [],
            "optimization_recommendations": [],
            "extracted_entities": {},
            "ats_breakdown": [],
            "feedback_history": {},
            "section_confidences": {},
            "section_diagnostics": {},
            "recruiter_score": 90,
            "ats_weaknesses": ["Docker"]
        }
        mock_resumes_collection.find_one.return_value = mock_resume

        response = self.client.get(f"/resumes/{resume_id}")
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertEqual(res_data["filename"], "resume1.pdf")
        self.assertEqual(res_data["recruiter_score"], 90)
        self.assertIn("Docker", res_data["ats_weaknesses"])

    @patch("routes.auth.users_collection")
    def test_get_and_post_preferences(self, mock_users_collection):
        # 1. Test GET /auth/preferences
        mock_user_doc = {
            "email": "test@example.com",
            "career_preferences": {
                "preferred_roles": ["Software Engineer"],
                "preferred_technologies": ["Python", "FastAPI"],
                "experience_level": "Intermediate",
                "preferred_industries": ["Tech"],
                "expected_salary": "$100k",
                "remote_preference": "Remote",
                "location_preference": "San Francisco"
            }
        }
        mock_users_collection.find_one.return_value = mock_user_doc

        response = self.client.get("/auth/preferences")
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertEqual(res_data["preferred_roles"], ["Software Engineer"])

        # 2. Test POST /auth/preferences
        payload = {
            "preferred_roles": ["Backend Developer"],
            "preferred_technologies": ["FastAPI", "MongoDB"],
            "experience_level": "Senior",
            "preferred_industries": ["Finance"],
            "expected_salary": "$150k",
            "remote_preference": "Hybrid",
            "location_preference": "New York"
        }
        response = self.client.post("/auth/preferences", json=payload)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertEqual(res_data["message"], "Preferences saved successfully")
        self.assertEqual(res_data["preferences"]["preferred_roles"], ["Backend Developer"])

    @patch("routes.interviews.resumes_collection")
    @patch("routes.interviews.interview_sessions_collection")
    def test_start_interview(self, mock_sessions_collection, mock_resumes_collection):
        resume_id = "60d0fe4f5311236168e109cb"
        mock_resume = {
            "_id": ObjectId(resume_id),
            "user_email": "test@example.com",
            "filename": "resume1.pdf"
        }
        mock_resumes_collection.find_one.return_value = mock_resume

        payload = {
            "resume_id": resume_id,
            "job_title": "FastAPI Developer",
            "difficulty": "Intermediate",
            "mode": "Technical"
        }

        # Mock generator and builders to avoid Gemini calls
        with patch("interviews.interview_context_builder.InterviewContextBuilder.build_interview_context") as mock_context, \
             patch("interviews.resume_question_generator.ResumeQuestionGenerator.generate_questions") as mock_questions:
            
            mock_context.return_value = {"skills": ["React"], "experience": []}
            mock_questions.return_value = [
                {"question": "Explain React state.", "ideal_concepts": ["state", "hooks"]}
            ]

            response = self.client.post("/interviews/start", json=payload)
            self.assertEqual(response.status_code, 200)
            res_data = response.json()
            self.assertEqual(res_data["job_title"], "FastAPI Developer")
            self.assertEqual(res_data["mode"], "Technical")
            self.assertEqual(len(res_data["questions"]), 1)
            self.assertEqual(res_data["questions"][0]["question"], "Explain React state.")

    @patch("routes.live_jobs.resumes_collection")
    def test_live_jobs_recommendations(self, mock_resumes_collection):
        resume_id = "60d0fe4f5311236168e109cb"
        mock_resume = {
            "_id": ObjectId(resume_id),
            "user_email": "test@example.com",
            "skills": ["React", "FastAPI"]
        }
        mock_resumes_collection.find_one.return_value = mock_resume

        # Mock CareerPreferenceEngine and JobPreferenceMatcher to return custom test results
        with patch("jobs.career_preference_engine.CareerPreferenceEngine.get_preferences") as mock_prefs, \
             patch("routes.live_jobs.fetch_and_cache_jobs") as mock_fetch:
            
            mock_prefs.return_value = {
                "preferred_roles": ["FastAPI Developer"],
                "preferred_technologies": ["React", "FastAPI"],
                "experience_level": "Intermediate",
                "preferred_industries": ["Tech"],
                "expected_salary": "$100k",
                "remote_preference": "Remote",
                "location_preference": "Any"
            }
            mock_fetch.return_value = [
                {
                    "id": "job_1",
                    "title": "Remote React Developer",
                    "company_name": "Tech Corp",
                    "category": "software-development",
                    "candidate_required_location": "Remote",
                    "salary": "$90k - $120k",
                    "url": "https://remotive.com",
                    "description": "Develop interfaces using React."
                }
            ]

            response = self.client.get(f"/live-jobs/recommendations?resume_id={resume_id}")
            self.assertEqual(response.status_code, 200)
            res_data = response.json()
            self.assertTrue(len(res_data) > 0)
            self.assertEqual(res_data[0]["title"], "Remote React Developer")
            self.assertIn("match_percentage", res_data[0])
            self.assertIn("skill_gaps", res_data[0])

if __name__ == '__main__':
    unittest.main()
