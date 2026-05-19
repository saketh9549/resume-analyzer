"""
Application constants
"""

# API Keys
OPENAI_API_KEY = ""
GEMINI_API_KEY = ""

# Database
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "resume_analyzer"

# File uploads
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FORMATS = ['pdf', 'docx', 'txt']

# ATS thresholds
GOOD_ATS_SCORE = 75
EXCELLENT_ATS_SCORE = 90
