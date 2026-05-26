import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load from current directory's .env if present
load_dotenv()
# Fall back to checking root directory if MONGO_URI is missing
if not os.getenv("MONGO_URI"):
    load_dotenv(dotenv_path="../.env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
    # Set a 5-second timeout for server selection so it fails quickly if offline
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Trigger a connection check
    client.admin.command('ping')
    db = client["resume_analyzer"]
    users_collection = db["users"]
    resumes_collection = db["resumes"]
    print(f"MongoDB Connected Successfully to: {MONGO_URI}")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to connect to MongoDB at {MONGO_URI}. Reason: {e}")
    # Define fallback mock objects to prevent importing modules from crashing,
    # but actual database operations will fail gracefully.
    db = None
    users_collection = None
    resumes_collection = None