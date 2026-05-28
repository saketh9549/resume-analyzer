import os
from pymongo import MongoClient
from dotenv import load_dotenv

# ARCHITECTURE NOTE:
# This module uses the synchronous pymongo.MongoClient for all database operations.
# While the backend is built on async FastAPI, blocking pymongo calls are used here
# for simplicity and backward compatibility. Under heavy concurrent load this can
# cause event loop starvation. A future migration to motor.AsyncIOMotorClient across
# all routes is recommended for production-grade scalability.
#
# The async motor driver in database/connection.py is used ONLY for index creation
# during application startup and is NOT used for runtime query operations.

from config.settings import settings

MONGO_URI = settings.MONGO_URI
MONGO_DB = settings.MONGO_DB

import logging

logger = logging.getLogger(__name__)

# Initialize MongoClient lazily. It will NOT establish a connection until the first query.
# This prevents synchronous network blocking during FastAPI's async startup.
try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    users_collection = db["users"]
    resumes_collection = db["resumes"]
except Exception as e:
    logger.error(f"CRITICAL ERROR: Failed to initialize MongoDB sync client: {e}")
    db = None
    users_collection = None
    resumes_collection = None