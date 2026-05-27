import sys
import os
import unittest

# Add backend directory to Python path to enable correct package imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# pyrefly: ignore [missing-import]
from services.resume_service import analyze_resume_text

class TestATSScore(unittest.TestCase):
    def test_ats_score_calculation(self):
        # Empty text should return a baseline score of 45
        result_empty = analyze_resume_text("")
        self.assertEqual(result_empty["score"], 45)
        self.assertEqual(len(result_empty["skills_found"]), 0)

        # Rich text with skills and section headers should yield a high score
        full_text = """
        John Doe
        Experience:
        Worked as React Developer and used Python and FastAPI.
        We deployed containers with Docker and AWS.
        Used Git for version control and PostgreSQL.
        Education:
        BS Computer Science
        Projects:
        Built a SaaS using JavaScript and Tailwind.
        Skills:
        React, Python, FastAPI, Docker, AWS, Git, PostgreSQL, JavaScript
        """
        result_full = analyze_resume_text(full_text)
        self.assertGreater(result_full["score"], 70)
        self.assertTrue("React" in result_full["skills_found"])

class TestKeywordMatch(unittest.TestCase):
    def test_keyword_matching(self):
        text = "Experienced in Python coding and React web application design."
        result = analyze_resume_text(text)

        # Skills found should include React and Python
        self.assertIn("React", result["skills_found"])
        self.assertIn("Python", result["skills_found"])

        # Skills found should NOT include AWS as it is absent
        self.assertNotIn("AWS", result["skills_found"])

if __name__ == '__main__':
    unittest.main()

