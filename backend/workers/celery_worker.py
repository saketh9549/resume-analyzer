import os
import logging
from celery import Celery

logger = logging.getLogger(__name__)

# Load Redis configs from environment variables, default to loopback
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app context
celery_app = Celery(
    "resume_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["workers.tasks"]
)

# Optional configuration settings
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 minutes max per task
)

def is_redis_available() -> bool:
    """
    Checks if the Redis broker is reachable.
    Used by routing APIs to dynamically decide whether to execute tasks in background 
    or fall back to immediate inline processing to avoid user hang ups.
    """
    try:
        import redis
        r = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=2)
        r.ping()
        return True
    except Exception:
        logger.warning("Redis broker appears offline. Falling back to inline API execution.")
        return False
