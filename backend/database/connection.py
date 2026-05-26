import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

# Load configuration variables from dotenv file
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Database connection manager for async Motor connection pool.
    """
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect_to_database(cls, uri: str = None, db_name: str = None) -> AsyncIOMotorDatabase:
        """
        Establishes connection to MongoDB database and triggers index initialization.
        """
        if not uri:
            uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        if not db_name:
            db_name = os.getenv("MONGO_DB", "resume_analyzer")

        logger.info(f"Connecting to MongoDB at URI: {uri}")
        try:
            # Set a 5-second timeout limit for connections to fail fast if port is blocked
            cls.client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
            cls.db = cls.client[db_name]
            
            # Send server ping command to verify database handshake
            await cls.client.admin.command("ping")
            logger.info("MongoDB Connection pinged successfully. Connected established.")
            
            # Automated indexing compilation
            await cls.create_indexes()
            return cls.db
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Failed connection check to MongoDB: {e}")
            raise e

    @classmethod
    async def close_database_connection(cls):
        """
        Gracefully closes MongoClient socket connections.
        """
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB Client connection pool.")

    @classmethod
    async def create_indexes(cls):
        """
        Asynchronously creates required collections indexes to support high throughput lookup queries.
        """
        if cls.db is None:
            raise RuntimeError("Database connection not initialized prior to index creation request.")

        logger.info("Initializing index creation...")
        try:
            # 1. Enforce unique index on identity keys (users.email)
            users_index = await cls.db["users"].create_index("email", unique=True)
            logger.info(f"Index created on users.email: {users_index}")

            # 2. Fast relational aggregation for user specific lookups (resumes.user_id)
            resumes_index = await cls.db["resumes"].create_index("user_id")
            logger.info(f"Index created on resumes.user_id: {resumes_index}")

            # 3. High-throughput sort index for platform ranking engines (resume_scores.ats_score descending)
            scores_index = await cls.db["resume_scores"].create_index([("ats_score", -1)])
            logger.info(f"Index created on resume_scores.ats_score: {scores_index}")

            # 4. Fast lookup for AI feedback linked to specific resumes
            ai_feedback_index = await cls.db["ai_feedback"].create_index("resume_id")
            logger.info(f"Index created on ai_feedback.resume_id: {ai_feedback_index}")

            # 5. Fast lookup for job matches linked to specific resumes
            job_matches_index = await cls.db["job_matches"].create_index("resume_id")
            logger.info(f"Index created on job_matches.resume_id: {job_matches_index}")

            # 6. Enterprise indexing
            await cls.db["interview_sessions"].create_index("user_email")
            await cls.db["interview_sessions"].create_index("resume_id")
            await cls.db["shortlists"].create_index("recruiter_email", unique=True)
            await cls.db["rewrite_history"].create_index("resume_id")
            await cls.db["embeddings_cache"].create_index("hash", unique=True)
            await cls.db["live_jobs_cache"].create_index("type", unique=True)
            logger.info("Enterprise collections indexed successfully.")

            logger.info("MongoDB indexing initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to compile database collection indexes: {e}")
            raise e

# Database dependency injection helper for FastAPI routes
async def get_db() -> AsyncIOMotorDatabase:
    if DatabaseConnection.db is None:
        raise RuntimeError("Database connection has not been initialized.")
    return DatabaseConnection.db
