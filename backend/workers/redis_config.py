import os
import logging
import redis

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_redis_client():
    """
    Returns a configured Redis client instance.
    """
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)

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
