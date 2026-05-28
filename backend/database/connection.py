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
            uri = os.getenv("MONGO_URI")
            if not uri:
                raise ValueError("CRITICAL ERROR: MONGO_URI environment variable is missing. Check your Render configuration.")
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

            # Additional search and sort indexes for resumes
            await cls.db["resumes"].create_index("user_email")
            await cls.db["resumes"].create_index([("upload_date", -1)])
            await cls.db["resumes"].create_index([("ats_score", -1)])
            logger.info("Additional indexes compiled on resumes collection (user_email, upload_date, ats_score).")

            # 3. High-throughput sort index for platform ranking engines (resume_scores.ats_score descending)
            scores_index = await cls.db["resume_scores"].create_index([("ats_score", -1)])
            logger.info(f"Index created on resume_scores.ats_score: {scores_index}")

            # 4. Fast lookup for AI feedback linked to specific resumes
            ai_feedback_index = await cls.db["ai_feedback"].create_index("resume_id")
            logger.info(f"Index created on ai_feedback.resume_id: {ai_feedback_index}")

            # 5. Fast lookup for job matches linked to specific resumes
            job_matches_index = await cls.db["job_matches"].create_index("resume_id")
            await cls.db["job_matches"].create_index([("semantic_score", -1)])
            logger.info(f"Indexes created on job_matches: resume_id and semantic_score.")

            # 6. Enterprise indexing
            await cls.db["interview_sessions"].create_index("user_email")
            await cls.db["interview_sessions"].create_index("resume_id")
            await cls.db["shortlists"].create_index("recruiter_email", unique=True)
            await cls.db["rewrite_history"].create_index("resume_id")
            await cls.db["embeddings_cache"].create_index("hash", unique=True)
            await cls.db["live_jobs_cache"].create_index("type", unique=True)
            logger.info("Enterprise collections indexed successfully.")

            # 7. Performance indexes for missing query patterns
            # Recruiter jobs sorted by created_at (recruiter_email already filters)
            await cls.db["recruiter_jobs"].create_index("recruiter_email")
            await cls.db["recruiter_jobs"].create_index([("recruiter_email", 1), ("created_at", -1)])

            # Refresh token lookup by token value (rotating token pattern)
            try:
                await cls.db["refresh_tokens"].delete_many({"token": {"$in": [None, ""]}})
                duplicates = await cls.db["refresh_tokens"].aggregate([
                    {"$group": {"_id": "$token", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
                    {"$match": {"count": {"$gt": 1}}}
                ]).to_list(None)
                for dup in duplicates:
                    for doc_id in dup["ids"][1:]:
                        await cls.db["refresh_tokens"].delete_one({"_id": doc_id})
            except Exception as cleanup_err:
                logger.warning(f"Failed to pre-clean duplicate refresh tokens: {cleanup_err}")

            await cls.db["refresh_tokens"].create_index("token", unique=True)
            await cls.db["refresh_tokens"].create_index("email")

            # OTP lookup indexes for password reset and email verification
            await cls.db["password_resets"].create_index([("email", 1), ("otp", 1)])
            await cls.db["email_verifications"].create_index([("email", 1), ("otp", 1)])

            # Interview sessions sort by created_at (user_email already indexed)
            await cls.db["interview_sessions"].create_index([("user_email", 1), ("created_at", -1)])

            # Compound index for the most common resume query pattern:
            # find by user_email + sort by upload_date  (covers /list, /recent, /stats)
            await cls.db["resumes"].create_index([("user_email", 1), ("upload_date", -1)])

            # Career intelligence compound lookup
            await cls.db["career_intelligence"].create_index(
                [("resume_id", 1), ("target_role", 1), ("type", 1)]
            )

            logger.info("Performance indexes compiled successfully.")

        except Exception as e:
            logger.error(f"Failed to compile database collection indexes: {e}")
            raise e

# Database dependency injection helper for FastAPI routes
async def get_db() -> AsyncIOMotorDatabase:
    if DatabaseConnection.db is None:
        raise RuntimeError("Database connection has not been initialized.")
    return DatabaseConnection.db
