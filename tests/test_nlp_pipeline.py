import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from nlp.text_preprocessor import preprocess_text, lemmatize_word, clean_text
from nlp.section_classifier import SectionClassifier
from nlp.entity_extractor import EntityExtractor
from nlp.ats_matrix import calculate_weighted_score
from nlp.semantic_match_engine import SemanticMatchEngine

class TestTextPreprocessor(unittest.TestCase):
    def test_clean_text(self):
        text = "Backend   services\u200b developed  "
        self.assertEqual(clean_text(text), "Backend services developed")

    def test_lemmatize_word(self):
        self.assertEqual(lemmatize_word("developing"), "develop")
        self.assertEqual(lemmatize_word("developed"), "develop")
        self.assertEqual(lemmatize_word("technologies"), "technology")
        self.assertEqual(lemmatize_word("systems"), "system")

    def test_preprocess_text(self):
        text = "We are developing REST APIs using FastAPI."
        processed = preprocess_text(text)
        self.assertIn("develop", processed)
        self.assertIn("rest", processed)
        self.assertIn("fastapi", processed)
        self.assertNotIn("we", processed)
        self.assertNotIn("are", processed)


class TestSectionClassifier(unittest.TestCase):
    def test_classify_by_heuristics(self):
        heading, confidence = SectionClassifier.classify_by_heuristics("## 1. Professional Experience")
        self.assertEqual(heading, "experience")
        self.assertGreaterEqual(confidence, 0.8)

        heading_skills, confidence_skills = SectionClassifier.classify_by_heuristics("Technical Skills")
        self.assertEqual(heading_skills, "skills")
        self.assertGreaterEqual(confidence_skills, 0.8)

    def test_segment_resume(self):
        resume_text = (
            "John Doe\n"
            "john@example.com | 123-456-7890\n"
            "Summary\n"
            "Experienced backend engineer specializing in cloud platforms.\n"
            "Skills\n"
            "Python, FastAPI, Docker, AWS\n"
            "Experience\n"
            "Senior Backend Developer at Google (2022 - 2026)\n"
            "Education\n"
            "Bachelor of Science in Computer Science from MIT\n"
        )
        result = SectionClassifier.segment_resume(resume_text)
        self.assertIn("sections", result)
        self.assertIn("confidences", result)
        self.assertIn("diagnostics", result)
        
        sections = result["sections"]
        self.assertIn("contact", sections)
        self.assertIn("summary", sections)
        self.assertIn("skills", sections)
        self.assertIn("experience", sections)
        self.assertIn("education", sections)


class TestEntityExtractor(unittest.TestCase):
    def test_extract_all_entities(self):
        text = (
            "Highly accomplished software engineer with 4 years of experience.\n"
            "Worked at Google in San Francisco as a Senior Software Engineer.\n"
            "Possess AWS Certified Developer Associate certification.\n"
            "Developed high performance REST APIs using React, Python, and Django.\n"
            "Optimized SQL query response times by 35% using database indexing."
        )
        extractor = EntityExtractor()
        entities = extractor.extract_all_entities(text)
        
        self.assertIn("programming_languages", entities)
        self.assertIn("frameworks", entities)
        self.assertIn("companies", entities)
        self.assertIn("locations", entities)
        self.assertIn("certifications", entities)
        self.assertIn("achievements", entities)
        self.assertIn("years_of_experience", entities)

        # Check values
        languages = [x["value"] for x in entities["programming_languages"]]
        self.assertIn("Python", languages)

        frameworks = [x["value"] for x in entities["frameworks"]]
        self.assertIn("React", frameworks)
        self.assertIn("Django", frameworks)

        companies = [x["value"] for x in entities["companies"]]
        self.assertIn("Google", companies)

        certs = [x["value"] for x in entities["certifications"]]
        self.assertTrue(any("aws" in c.lower() for c in certs))

        achievements = [x["value"] for x in entities["achievements"]]
        self.assertTrue(any("35%" in a for a in achievements))


class TestATSMatrix(unittest.TestCase):
    def test_calculate_weighted_score(self):
        category_scores = {
            "skills_match": 85.0,
            "semantic_relevance": 90.0,
            "experience_quality": 80.0,
            "resume_formatting": 95.0,
            "section_completeness": 90.0,
            "action_verb_strength": 85.0,
            "achievement_quality": 75.0,
            "readability": 90.0,
            "keyword_coverage": 80.0,
            "recruiter_relevance": 85.0
        }
        score = calculate_weighted_score(category_scores)
        self.assertGreaterEqual(score, 10)
        self.assertLessEqual(score, 99)


class TestSemanticMatchEngine(unittest.IsolatedAsyncioTestCase):
    async def test_match_resume_to_job(self):
        resume_data = {
            "skills": ["Python", "FastAPI", "Docker", "SQL"],
            "experience": [
                {
                    "job_title": "Software Engineer",
                    "company": "Tech Corp",
                    "responsibilities": ["Developed backend REST APIs using Python and FastAPI"]
                }
            ],
            "projects": [
                {
                    "name": "Cloud App",
                    "description": "Hosted a React application on AWS cloud infrastructure"
                }
            ]
        }
        job_details = {
            "job_title": "FastAPI Developer",
            "description": "We are looking for a software engineer to build REST APIs in Python using FastAPI.",
            "required_skills": ["Python", "FastAPI", "Docker", "AWS"],
            "experience_years_required": 2,
            "experience_level": "Intermediate"
        }
        
        result = await SemanticMatchEngine.match_resume_to_job(resume_data, job_details)
        self.assertIn("overall_score", result)
        self.assertIn("readiness_level", result)
        self.assertIn("semantic_similarity_score", result)
        self.assertIn("keyword_score", result)
        self.assertIn("contextual_relevance_score", result)
        self.assertIn("recruiter_relevance_score", result)
        self.assertIn("matching_skills", result)
        self.assertIn("missing_skills", result)


if __name__ == '__main__':
    unittest.main()
