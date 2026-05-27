import time
import logging
from fastapi import Request, HTTPException, status
from workers.celery_worker import is_redis_available
from workers.redis_config import get_redis_client

logger = logging.getLogger(__name__)

# Default rate limits: 100 requests per minute
LIMIT_WINDOW = 60  # seconds
LIMIT_MAX_REQUESTS = 100

async def rate_limiter(request: Request):
    """
    Enforces request rate limits using a Redis sorted set sliding window.
    Gracefully bypasses checks if Redis is offline.
    """
    if not is_redis_available():
        return

    try:
        r = get_redis_client()
        client_ip = request.client.host if request.client else "unknown_ip"
        route_path = request.url.path
        
        # Redis key format segmenting by client IP and request route
        redis_key = f"rate_limit:{client_ip}:{route_path}"
        current_time = int(time.time())
        
        # Clear out timestamps older than the sliding window boundary
        pipe = r.pipeline()
        pipe.zremrangebyscore(redis_key, 0, current_time - LIMIT_WINDOW)
        pipe.zadd(redis_key, {str(current_time): current_time})
        pipe.zcard(redis_key)
        pipe.expire(redis_key, LIMIT_WINDOW + 10)
        
        # Execute atomic sliding window updates
        results = pipe.execute()
        request_count = results[2]
        
        if request_count > LIMIT_MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded: {client_ip} tried calling {route_path} ({request_count} requests)")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down and try again later."
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Rate limiting failure: {e}. Bypassing check.")
        return
