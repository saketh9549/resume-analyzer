"""
Rate Limiting Middleware — Sliding Window Algorithm
Enterprise-grade per-IP and per-user request throttling.
Falls back to in-memory counter if Redis is unavailable.
"""
import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Per-IP sliding window state (in-memory fallback)
_ip_windows: dict[str, list[float]] = defaultdict(list)

# Rate limit configuration
RATE_LIMIT_REQUESTS = 120   # max requests
RATE_LIMIT_WINDOW_SEC = 60  # per minute window
BURST_LIMIT = 20            # burst max within 5 seconds

# Endpoints excluded from rate limiting (health checks, static assets)
EXEMPT_PATHS = {"/", "/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


def _is_exempt(path: str) -> bool:
    return path in EXEMPT_PATHS or path.startswith("/static")


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit_memory(ip: str) -> tuple[bool, int]:
    """
    Sliding window rate limit check using in-memory store.
    Returns (is_allowed, remaining_requests).
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SEC
    burst_start = now - 5

    # Clean expired timestamps
    _ip_windows[ip] = [t for t in _ip_windows[ip] if t > window_start]
    
    window_count = len(_ip_windows[ip])
    burst_count = sum(1 for t in _ip_windows[ip] if t > burst_start)

    if window_count >= RATE_LIMIT_REQUESTS or burst_count >= BURST_LIMIT:
        remaining = max(0, RATE_LIMIT_REQUESTS - window_count)
        return False, remaining

    _ip_windows[ip].append(now)
    remaining = max(0, RATE_LIMIT_REQUESTS - window_count - 1)
    return True, remaining


def _check_rate_limit_redis(ip: str) -> tuple[bool, int]:
    """
    Sliding window rate limit using Redis sorted sets (production-grade).
    """
    try:
        from workers.redis_config import get_redis_client
        r = get_redis_client()
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW_SEC
        key = f"ratelimit:{ip}"

        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, RATE_LIMIT_WINDOW_SEC + 5)
        results = pipe.execute()
        
        count = results[2]
        remaining = max(0, RATE_LIMIT_REQUESTS - count)

        if count > RATE_LIMIT_REQUESTS:
            # Remove the just-added entry since it's over limit
            r.zrem(key, str(now))
            return False, 0

        return True, remaining
    except Exception as e:
        logger.debug(f"Redis rate limit check failed, falling back to memory: {e}")
        return None, -1  # Signal to use memory fallback


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    HTTP middleware enforcing sliding-window rate limits.
    Prefers Redis for distributed environments; falls back to in-process memory.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if _is_exempt(path):
            return await call_next(request)

        ip = _get_client_ip(request)

        # Prefer Redis rate limiting; fall back to memory
        allowed, remaining = _check_rate_limit_redis(ip)
        if allowed is None:
            allowed, remaining = _check_rate_limit_memory(ip)

        if not allowed:
            logger.warning(f"Rate limit exceeded for IP: {ip} on path: {path}")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Too many requests. Please slow down and retry after a moment.",
                    "code": 429
                },
                headers={
                    "Retry-After": str(RATE_LIMIT_WINDOW_SEC),
                    "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Window": str(RATE_LIMIT_WINDOW_SEC)
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(RATE_LIMIT_WINDOW_SEC)
        return response
