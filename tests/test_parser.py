import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.resume_service import extract_text_from_pdf, analyze_resume_text

class TestPDFParser(unittest.TestCase):
    def test_parse_invalid_pdf_path(self):
        # Parsing a non-existent PDF should return an empty string gracefully
        text = extract_text_from_pdf("non_existent_file_path.pdf")
        self.assertEqual(text, "")

class TestDocxParser(unittest.TestCase):
    def test_fallback_plain_text(self):
        # Verify parser handles standard plain text mock documents correctly
        text = "Name: Jane Doe\nSkills: Python, Git"
        analysis = analyze_resume_text(text)
        self.assertIn("Python", analysis["skills_found"])
        self.assertIn("Git", analysis["skills_found"])

if __name__ == '__main__':
    unittest.main()

