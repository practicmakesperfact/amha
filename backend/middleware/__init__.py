"""
Middleware package init.
"""
from backend.middleware.rate_limiter import is_rate_limited

__all__ = ["is_rate_limited"]
