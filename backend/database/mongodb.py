from pymongo import MongoClient
from dotenv import load_dotenv

import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["resume_analyzer"]

users_collection = db["users"]

resumes_collection = db["resumes"]

print("MongoDB Connected Successfully")