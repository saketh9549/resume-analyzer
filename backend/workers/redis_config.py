import logging
import redis
from config.settings import settings

logger = logging.getLogger(__name__)

def get_redis_client():
    """
    Returns a configured Redis client instance.
    """
    if not settings.REDIS_URL:
        raise ValueError("REDIS_URL is not configured.")
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def is_redis_active() -> bool:
    """
    Checks if Redis server is active and responding to PING.
    """
    try:
        r = get_redis_client()
        r.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis is currently inactive: {e}")
        return False

def publish_event(channel: str, message: dict):
    """
    Publishes an event message payload as JSON string to Redis Pub/Sub channel.
    """
    import json
    try:
        r = get_redis_client()
        r.publish(channel, json.dumps(message))
    except Exception as e:
        logger.error(f"Failed to publish event to Redis: {e}")
