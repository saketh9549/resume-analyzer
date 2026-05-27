import sys
import os
import unittest
import warnings

# Suppress FutureWarnings and ResourceWarnings
warnings.simplefilter("ignore", category=FutureWarning)
warnings.simplefilter("ignore", category=ResourceWarning)

# Mongo cleanup is handled centrally in tests/__init__.py

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

# pyrefly: ignore [missing-import]
from multimodal.layout_scoring import LayoutScorer
# pyrefly: ignore [missing-import]
from multimodal.readability_engine import ReadabilityEngine
# pyrefly: ignore [missing-import]
from multimodal.pdf_image_extractor import convert_pdf_to_images
# pyrefly: ignore [missing-import]
from rag.chunking_engine import ChunkingEngine
# pyrefly: ignore [missing-import]
from rag.prompt_builder import PromptBuilder

class TestPDFImageExtractor(unittest.TestCase):
    def test_invalid_pdf_path(self):
        # Verify that converting a non-existent PDF returns an empty list and does not crash
        images = convert_pdf_to_images("non_existent_file.pdf")
        self.assertEqual(images, [])

class TestLayoutScorer(unittest.TestCase):
    def test_calculate_local_layout_scores(self):
        parsed = {
            "skills": ["Python", "FastAPI"],
            "education": [{"degree": "B.Tech"}],
            "experience": [{"role": "Backend Engineer"}],
            "projects": [{"title": "Analyzer"}],
            "contact": {"email": "test@test.com", "name": "Tester"}
        }
        text = "Hello world! This is a test resume block."
        scores = LayoutScorer.calculate_local_layout_scores(parsed, text)
        
        self.assertIn("structure_index", scores)
        self.assertIn("density_balance_score", scores)
        self.assertIn("contact_completeness_score", scores)
        self.assertIn("local_layout_quality", scores)
        self.assertEqual(scores["structure_index"], 100) # all 4 required sections present
        self.assertEqual(scores["contact_completeness_score"], 50) # 2 out of 4 contact fields filled

class TestReadabilityEngine(unittest.TestCase):
    def test_calculate_flesch_reading_ease(self):
        text = "The quick brown fox jumps over the lazy dog."
        score = ReadabilityEngine.calculate_flesch_reading_ease(text)
        self.assertTrue(0.0 <= score <= 100.0)

    def test_get_readability_metrics(self):
        text = "Standard paragraph readability text block."
        metrics = ReadabilityEngine.get_readability_metrics(text)
        self.assertIn("flesch_reading_ease_score", metrics)
        self.assertIn("readability_difficulty_level", metrics)
        self.assertIn("word_count", metrics)

class TestRAGChunking(unittest.TestCase):
    def test_chunk_text_sizes(self):
        text = "One two three four five six seven eight nine ten eleven twelve thirteen."
        chunks = ChunkingEngine.chunk_text(text, chunk_size=20, overlap=5)
        self.assertTrue(len(chunks) > 0)
        
    def test_chunk_empty_text(self):
        chunks = ChunkingEngine.chunk_text("")
        self.assertEqual(chunks, [])

class TestRAGPromptBuilder(unittest.TestCase):
    async def _run_build_rag_prompt(self):
        # Verify that the builder compiles prompt correctly
        orig = "Write a cover letter."
        prompt, sys = await PromptBuilder.build_rag_prompt(
            original_prompt=orig,
            query="non_existent_key",
            system_instruction="Default Instruction",
            limit=1
        )
        self.assertIn(orig, prompt)
        self.assertIn("augmented by our Career Intelligence Database", sys)

    def test_async_run(self):
        import asyncio
        asyncio.run(self._run_build_rag_prompt())

if __name__ == '__main__':
    unittest.main()
