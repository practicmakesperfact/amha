"""
Redis connection and utilities for AMHABINGO Bot.
Used for FSM state, rate limiting, and temporary sessions.
"""

import time
from redis.asyncio import Redis, from_url
from redis.exceptions import ConnectionError as RedisConnectionError
from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class InMemoryRedisPipeline:
    def __init__(self, db: "InMemoryRedisMock"):
        self.db = db
        self.actions = []

    def zremrangebyscore(self, key: str, min_score: float, max_score: float):
        def action():
            zset = self.db._zsets.setdefault(key, {})
            to_remove = [m for m, s in zset.items() if min_score <= s <= max_score]
            for m in to_remove:
                zset.pop(m)
            return len(to_remove)
        self.actions.append(action)
        return self

    def zadd(self, key: str, mapping: dict):
        def action():
            zset = self.db._zsets.setdefault(key, {})
            for m, s in mapping.items():
                zset[m] = s
            return len(mapping)
        self.actions.append(action)
        return self

    def zcard(self, key: str):
        def action():
            zset = self.db._zsets.get(key, {})
            return len(zset)
        self.actions.append(action)
        return self

    def expire(self, key: str, ttl: int):
        def action():
            return True
        self.actions.append(action)
        return self

    async def execute(self) -> list:
        return [act() for act in self.actions]


class InMemoryRedisMock:
    def __init__(self):
        self._data = {}
        self._ttls = {}
        self._zsets = {}
        logger.warning("Using in-memory Redis simulator (FSM states will reset on bot restart)")

    async def get(self, key: str):
        now = time.time()
        if key in self._ttls and self._ttls[key] < now:
            self._data.pop(key, None)
            self._ttls.pop(key, None)
            return None
        return self._data.get(key)

    async def setex(self, key: str, ttl: int, value: str):
        self._data[key] = value
        self._ttls[key] = time.time() + ttl

    async def delete(self, *keys: str):
        count = 0
        for k in keys:
            if k in self._data:
                self._data.pop(k)
                self._ttls.pop(k, None)
                count += 1
            if k in self._zsets:
                self._zsets.pop(k)
                count += 1
        return count

    def pipeline(self):
        return InMemoryRedisPipeline(self)

    async def aclose(self) -> None:
        pass


_redis_client = None


async def get_redis():
    """Return a singleton Redis client, falling back to in-memory if connection fails."""
    global _redis_client
    if _redis_client is None:
        if settings.REDIS_URL.startswith("memory://") or not settings.REDIS_URL:
            _redis_client = InMemoryRedisMock()
        else:
            try:
                client = from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                )
                # Test connection immediately
                await client.ping()
                _redis_client = client
                logger.info("Successfully connected to Redis", url=settings.REDIS_URL)
            except Exception as e:
                logger.warning(
                    "Could not connect to Redis server. Falling back to built-in in-memory FSM state tracker.",
                    url=settings.REDIS_URL,
                    error=str(e),
                )
                _redis_client = InMemoryRedisMock()
    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed")
