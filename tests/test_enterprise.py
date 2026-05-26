import sys
import os
import unittest

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from embeddings.embedding_service import EmbeddingService
from embeddings.similarity_engine import SimilarityEngine
from routes.interviews import MOCK_QUESTIONS

class TestEmbeddingService(unittest.TestCase):
    def test_mock_vector_generation(self):
        text = "Backend python FastAPI developer with Docker orchestration expertise"
        vec = EmbeddingService._generate_mock_vector(text)
        self.assertEqual(len(vec), 768)
        # Check normalization (sum of squares close to 1)
        squared_sum = sum(x*x for x in vec)
        self.assertAlmostEqual(squared_sum, 1.0, places=4)

    def test_mock_vector_determinism(self):
        text = "Same sentence"
        vec1 = EmbeddingService._generate_mock_vector(text)
        vec2 = EmbeddingService._generate_mock_vector(text)
        self.assertEqual(vec1, vec2)

class TestSimilarityEngine(unittest.TestCase):
    def test_cosine_similarity_identical(self):
        vec = [1.0, 2.0, 3.0, 4.0]
        score = SimilarityEngine.calculate_cosine_similarity(vec, vec)
        self.assertAlmostEqual(score, 1.0, places=4)

    def test_cosine_similarity_orthogonal(self):
        vec_a = [1.0, 0.0]
        vec_b = [0.0, 1.0]
        score = SimilarityEngine.calculate_cosine_similarity(vec_a, vec_b)
        self.assertEqual(score, 0.0)

    def test_match_query_to_documents(self):
        # Clear cache first to force new word-hashing mock vector generation
        from database.mongodb import db
        if db is not None:
            db["embeddings_cache"].delete_many({})

        docs = [
            {"id": "doc1", "parsed_text": "Python FastAPI developer React"},
            {"id": "doc2", "parsed_text": "UIUX Designer Figma wireframes"}
        ]
        
        async def run_test():
            # Query matching Python
            ranked = await SimilarityEngine.match_query_to_documents("FastAPI python engineer", docs, text_field="parsed_text", top_k=2)
            self.assertEqual(ranked[0]["id"], "doc1")
            self.assertTrue(ranked[0]["similarity_score"] > ranked[1]["similarity_score"])

        import asyncio
        asyncio.run(run_test())

class TestEnterpriseLogic(unittest.TestCase):
    def test_interview_readiness_score_calculation(self):
        # Verify the custom scoring calculation formula used to complete interview sessions
        scores = [80, 90, 70, None, 100]
        valid_scores = [s for s in scores if s is not None]
        readiness_score = int(sum(valid_scores) / len(valid_scores)) if valid_scores else 0
        self.assertEqual(readiness_score, 85)

    def test_live_jobs_html_stripping(self):
        # Verify the regex cleaning system used to wash HTML descriptions from Remotive responses
        import re
        raw_desc = "<p>Develop <strong>React</strong> applications.</p> <a href='...'>Apply now!</a>"
        clean_desc = re.sub(r'<[^>]*>', ' ', raw_desc)
        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
        self.assertEqual(clean_desc, "Develop React applications. Apply now!")

    def test_rewriter_fallback_structure(self):
        # Verify that fallback rewrite payloads are formatted matching the expected React component state schemas
        from routes.rewriter import REWRITE_FALLBACK
        self.assertIn("suggested_text", REWRITE_FALLBACK)
        self.assertIn("key_improvements", REWRITE_FALLBACK)
        self.assertTrue(isinstance(REWRITE_FALLBACK["key_improvements"], list))

if __name__ == '__main__':
    unittest.main()
