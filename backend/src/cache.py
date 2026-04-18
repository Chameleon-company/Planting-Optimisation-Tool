import logging

from redis.asyncio import Redis, from_url

from src.config import settings

logger = logging.getLogger(__name__)
_redis: Redis | None = None


def get_redis() -> Redis | None:
    global _redis
    if _redis is None and settings.REDIS_URL:
        _redis = from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def get(key: str) -> str | None:
    redis = get_redis()
    if not redis:
        return None
    try:
        return await redis.get(key)
    except Exception as e:
        logger.warning("Redis get failed for key %s: %s", key, e)
        return None


async def set(key: str, value: str, ttl: int = 3600) -> None:
    redis = get_redis()
    if not redis:
        return
    try:
        await redis.set(key, value, ex=ttl)
    except Exception as e:
        logger.warning("Redis set failed for key %s: %s", key, e)


async def invalidate(*keys: str) -> None:
    redis = get_redis()
    if not redis:
        return
    try:
        await redis.delete(*keys)
    except Exception as e:
        logger.warning("Redis invalidate failed for keys %s: %s", keys, e)
