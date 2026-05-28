from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import warnings
import logging
import time
import os
import platform

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress deprecation warnings from google.generativeai (scheduled for migration to google.genai)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*google.generativeai.*")

from routes.auth import router as auth_router
from routes.resume import router as resume_router
from routes.ai import router as ai_router
from routes.jobs import router as jobs_router
from routes.rewriter import router as rewriter_router
from routes.interviews import router as interviews_router
from routes.live_jobs import router as live_jobs_router
from routes.recruiter import router as recruiter_router
from routes.career import router as career_router

import contextlib
from database.connection import DatabaseConnection

_startup_time = time.time()

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

app = FastAPI(
    title="ResumeAI Enterprise API",
    description="Enterprise-grade AI Resume Analysis, ATS Scoring, Career Intelligence & Recruiter Platform",
    version="2.0.0",
    lifespan=lifespan
)

# ── MIDDLEWARE STACK (order matters: outermost first) ──────────────────────

# 1. Request logging + error handlers
from middleware.request_logger import RequestLoggerMiddleware
from utils.error_handler import register_error_handlers

app.add_middleware(RequestLoggerMiddleware)
register_error_handlers(app)

# 2. Rate limiting (per-IP sliding window)
from middleware.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# 3. GZip response compression (min size 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1024)

# 4. CORS
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


# ── ROUTES ─────────────────────────────────────────────────────────────────

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
    resume_router,
    prefix="/resumes",
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

app.include_router(
    career_router,
    prefix="/career",
    tags=["Career Intelligence"]
)


# ── SYSTEM ENDPOINTS ───────────────────────────────────────────────────────

@app.get("/", tags=["System"])
def home():
    return {
        "message": "ResumeAI Enterprise Backend Running",
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/health", tags=["System"])
async def health_check():
    """
    Comprehensive health check endpoint for container orchestration (Docker/Kubernetes).
    Returns liveness status of all dependent services.
    """
    uptime_seconds = round(time.time() - _startup_time, 1)
    health = {
        "status": "healthy",
        "uptime_seconds": uptime_seconds,
        "version": "2.0.0",
        "services": {}
    }

    # Check MongoDB
    try:
        from database.mongodb import db
        if db is not None:
            db.command("ping")
            health["services"]["mongodb"] = "online"
        else:
            health["services"]["mongodb"] = "offline"
            health["status"] = "degraded"
    except Exception as e:
        health["services"]["mongodb"] = f"error: {str(e)[:60]}"
        health["status"] = "degraded"

    # Check Redis
    try:
        from workers.redis_config import is_redis_active
        health["services"]["redis"] = "online" if is_redis_active() else "offline"
    except Exception:
        health["services"]["redis"] = "offline"

    # Check Celery worker (via Redis broker)
    try:
        from workers.celery_worker import is_redis_available
        health["services"]["celery_broker"] = "online" if is_redis_available() else "offline"
    except Exception:
        health["services"]["celery_broker"] = "offline"

    return health


@app.get("/metrics", tags=["System"])
async def get_metrics():
    """
    Lightweight operational metrics for monitoring dashboards.
    Returns resume counts, active sessions, and system resource summary.
    """
    metrics = {
        "uptime_seconds": round(time.time() - _startup_time, 1),
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "resume_stats": {},
        "session_stats": {}
    }

    try:
        from database.mongodb import db
        if db is not None:
            metrics["resume_stats"]["total_resumes"] = db["resumes"].count_documents({})
            metrics["resume_stats"]["analyzed"] = db["resumes"].count_documents({"analysis_status": "analyzed"})
            metrics["resume_stats"]["queued"] = db["resumes"].count_documents({"analysis_status": "queued"})
            metrics["session_stats"]["total_interview_sessions"] = db["interview_sessions"].count_documents({})
            metrics["session_stats"]["total_users"] = db["users"].count_documents({})
            metrics["session_stats"]["total_job_matches"] = db["job_matches"].count_documents({})
    except Exception as e:
        metrics["resume_stats"]["error"] = str(e)[:60]

    # Memory usage (best-effort)
    try:
        import psutil
        proc = psutil.Process()
        mem = proc.memory_info()
        metrics["memory"] = {
            "rss_mb": round(mem.rss / 1024 / 1024, 1),
            "vms_mb": round(mem.vms / 1024 / 1024, 1)
        }
    except ImportError:
        metrics["memory"] = {"note": "psutil not installed"}
    except Exception:
        metrics["memory"] = {}

    return metrics