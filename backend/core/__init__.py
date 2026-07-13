"""
Core package init — re-exports for convenience.
"""
from backend.core.config import settings
from backend.core.logging import configure_logging, get_logger
from backend.core.redis import get_redis, close_redis

__all__ = [
    "settings",
    "configure_logging",
    "get_logger",
    "get_redis",
    "close_redis",
]
