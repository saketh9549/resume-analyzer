import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from jobs.skill_matcher import SkillMatcher
from jobs.semantic_matcher import SemanticMatcher
from jobs.scoring_engine import ScoringEngine

class TestSkillMatcher(unittest.TestCase):
    def test_skill_matcher_exact_case(self):
        user_skills = ["React", "Python", "Docker"]
        req_skills = ["React", "Python"]
        res = SkillMatcher.match_skills(user_skills, req_skills)
        self.assertEqual(res["match_ratio"], 100.0)
        self.assertEqual(res["matching_skills"], ["Python", "React"]) # sorted casing
        self.assertEqual(res["missing_skills"], [])
        self.assertEqual(res["extra_skills"], ["Docker"])

    def test_skill_matcher_case_insensitive(self):
        user_skills = ["react", "PYTHON"]
        req_skills = ["React", "Python", "Kubernetes"]
        res = SkillMatcher.match_skills(user_skills, req_skills)
        self.assertEqual(res["matching_skills"], ["Python", "React"])
        self.assertEqual(res["missing_skills"], ["Kubernetes"])
        self.assertEqual(res["match_ratio"], 66.7)

class TestSemanticMatcher(unittest.TestCase):
    def test_overlap_calculation(self):
        text = "Developed a real-time Chat Application using React, Node.js and Socket.io for active user message queues."
        keywords = ["React", "Socket.io", "Django"]
        overlap = SemanticMatcher.calculate_text_overlap(text, keywords)
        # Found React and Socket.io, missed Django
        self.assertEqual(overlap, 66.7)

class TestScoringEngine(unittest.TestCase):
    def test_experience_parse(self):
        exp = [
            {"duration": "2021 - 2024"},
            {"duration": "2025 - Present"},
            {"duration": ""}
        ]
        years = ScoringEngine.parse_experience_years(exp)
        # Job 1: 3.0 yrs. Job 2: 1.0 yrs (2026 - 2025). Job 3: 1.5 yrs. Total: 5.5 yrs
        self.assertEqual(years, 5.5)

    def test_evaluate_job_match(self):
        resume = {
            "skills": ["React", "Python", "MongoDB", "FastAPI"],
            "education": [{"degree": "Bachelor of Technology", "institution": "SNU"}],
            "projects": [{"title": "Resume Analyzer", "description": "FastAPI project using MongoDB"}],
            "experience": [{"duration": "2023 - Present"}], # 3 years
            "certifications": ["AWS Cloud Practitioner"],
            "ats_score": 80
        }
        
        job = {
            "job_title": "Backend Developer",
            "required_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
            "experience_level": "Intermediate",
            "experience_years_required": 3
        }
        
        res = ScoringEngine.evaluate_job_match(resume, job)
        self.assertEqual(res["job_title"], "Backend Developer")
        self.assertIn("Python", res["matching_skills"])
        self.assertIn("Docker", res["missing_skills"])
        self.assertTrue(0 <= res["match_percentage"] <= 100)
        
if __name__ == '__main__':
    unittest.main()
