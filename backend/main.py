from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.resume import router as resume_router
from routes.ai import router as ai_router
from routes.jobs import router as jobs_router
from routes.rewriter import router as rewriter_router
from routes.interviews import router as interviews_router
from routes.live_jobs import router as live_jobs_router
from routes.recruiter import router as recruiter_router

import contextlib
from database.connection import DatabaseConnection

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await DatabaseConnection.connect_to_database()
        try:
            from rag.knowledge_loader import KnowledgeLoader
            await KnowledgeLoader.seed_default_knowledge()
        except Exception as se:
            import logging
            logging.getLogger(__name__).error(f"Failed to seed default RAG knowledge: {se}")
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to connect to database on startup: {e}")
    yield
    await DatabaseConnection.close_database_connection()

app = FastAPI(lifespan=lifespan)


# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ROUTES
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)

app.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI Feedback"]
)

app.include_router(
    jobs_router,
    prefix="/jobs",
    tags=["Job Matching"]
)

app.include_router(
    rewriter_router,
    prefix="/rewriter",
    tags=["AI Rewriter"]
)

app.include_router(
    interviews_router,
    prefix="/interviews",
    tags=["AI Interview Prep"]
)

app.include_router(
    live_jobs_router,
    prefix="/live-jobs",
    tags=["Live Job API"]
)

app.include_router(
    recruiter_router,
    prefix="/recruiter",
    tags=["Recruiter Console"]
)

@app.get("/")
def home():
    return {
        "message": "Resume Analyzer Backend Running"
    }