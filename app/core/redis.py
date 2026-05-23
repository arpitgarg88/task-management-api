import redis.asyncio as redis
import logging
from app.core.config import settings


logger = logging.getLogger("cache")

REDIS_URL = settings.REDIS_URL

redis_client = None


async def init_redis():
    global redis_client
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        logger.info(f"[REDIS CONNECTED] {REDIS_URL}")
    except Exception as e:
        redis_client = None
        logger.warning(f"[REDIS INIT FAILED] {e}")


async def get_cache(key: str, context: dict = None):
    if not redis_client:
        return None

    try:
        value = await redis_client.get(key)

        if value:
            logger.info(f"[CACHE HIT] key={key} context={context}")
        else:
            logger.info(f"[CACHE MISS] key={key} context={context}")

        return value

    except Exception as e:
        logger.warning(f"[CACHE ERROR GET] key={key} err={e}")
        return None


async def set_cache(key: str, value: str, ttl: int = 300):
    if not redis_client:
        return

    try:
        await redis_client.setex(key, ttl, value)
        logger.info(f"[CACHE SET] key={key}")

    except Exception as e:
        logger.warning(f"[CACHE ERROR SET] key={key} err={e}")


async def delete_cache(key: str):
    if not redis_client:
        return

    try:
        await redis_client.delete(key)
        logger.info(f"[CACHE DELETE] key={key}")

    except Exception as e:
        logger.warning(f"[CACHE ERROR DELETE] key={key} err={e}")