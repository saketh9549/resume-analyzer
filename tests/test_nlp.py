import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.resume_service import analyze_resume_text

class TestSkillExtraction(unittest.TestCase):
    def test_skill_extraction(self):
        text = "Backend services developed using Java, C++, and Go."
        result = analyze_resume_text(text)
        self.assertIn("Java", result["skills_found"])
        self.assertIn("C++", result["skills_found"])
        self.assertIn("Go", result["skills_found"])

class TestExperienceExtraction(unittest.TestCase):
    def test_experience_extraction_detection(self):
        # The parser checks for key section titles like 'experience'
        text = "Experience: Senior Tech Lead (2020-2024)"
        result = analyze_resume_text(text)
        self.assertNotIn("experience", result["suggestions"])

if __name__ == '__main__':
    unittest.main()

