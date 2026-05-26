import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.response_parser import clean_gemini_json_string, parse_ai_response
from ai.prompts.feedback_prompt import get_feedback_prompt
from ai.gemini_service import FEEDBACK_FALLBACK

class TestAIResponseParser(unittest.TestCase):
    def test_clean_json_markdown_fences(self):
        raw = "```json\n{\"key\": \"value\"}\n```"
        cleaned = clean_gemini_json_string(raw)
        self.assertEqual(cleaned, "{\"key\": \"value\"}")

    def test_clean_json_extraneous_text(self):
        raw = "Here is the result:\n{\n  \"key\": \"value\"\n}\nHope this helps!"
        cleaned = clean_gemini_json_string(raw)
        self.assertEqual(cleaned, "{\n  \"key\": \"value\"\n}")

    def test_parse_response_with_fallback(self):
        raw_bad = "invalid json data string"
        parsed = parse_ai_response(raw_bad, FEEDBACK_FALLBACK)
        self.assertEqual(parsed["strengths"], FEEDBACK_FALLBACK["strengths"])

class TestAIPrompts(unittest.TestCase):
    def test_feedback_prompt_generation(self):
        data = {"skills": ["React"], "ats_score": 80}
        prompt = get_feedback_prompt(data)
        self.assertIn("React", prompt)
        self.assertIn("80", prompt)

if __name__ == '__main__':
    unittest.main()
