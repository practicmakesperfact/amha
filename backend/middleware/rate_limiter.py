"""
Rate limiting middleware using Redis sliding window algorithm.
Prevents spam and abuse per user.
"""

from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import BaseHandler, CallbackContext

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.redis import get_redis

logger = get_logger(__name__)

RATE_KEY_PREFIX = "rate:"


async def is_rate_limited(telegram_id: int) -> bool:
    """
    Sliding window rate limiting.
    Returns True if the user has exceeded the allowed request rate.
    """
    redis = await get_redis()
    key = f"{RATE_KEY_PREFIX}{telegram_id}"

    import time
    now = time.time()
    window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS

    # Use a sorted set: member=timestamp, score=timestamp
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)  # Remove old entries
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS + 1)
    results = await pipe.execute()

    request_count: int = results[2]
    if request_count > settings.RATE_LIMIT_MAX_REQUESTS:
        logger.warning(
            "Rate limit exceeded",
            telegram_id=telegram_id,
            count=request_count,
            max=settings.RATE_LIMIT_MAX_REQUESTS,
        )
        return True
    return False
