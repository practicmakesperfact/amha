"""
Redis-backed FSM (Finite State Machine) for conversation state management.
Each user has a conversation state and optional context data stored in Redis.
"""

import json
from enum import Enum
from typing import Any, Optional

from backend.core.logging import get_logger
from backend.core.redis import get_redis

logger = get_logger(__name__)

FSM_KEY_PREFIX = "fsm:state:"
FSM_DATA_PREFIX = "fsm:data:"
FSM_TTL_SECONDS = 3600  # 1 hour idle timeout


class UserState(str, Enum):
    """All possible conversation states."""

    IDLE = "IDLE"

    # Registration
    AWAITING_CONTACT = "AWAITING_CONTACT"

    # Deposit
    AWAITING_DEPOSIT_AMOUNT = "AWAITING_DEPOSIT_AMOUNT"
    AWAITING_DEPOSIT_SMS = "AWAITING_DEPOSIT_SMS"

    # Withdrawal
    AWAITING_WITHDRAWAL_PHONE = "AWAITING_WITHDRAWAL_PHONE"
    AWAITING_WITHDRAWAL_AMOUNT = "AWAITING_WITHDRAWAL_AMOUNT"

    # Transfer
    AWAITING_TRANSFER_RECIPIENT = "AWAITING_TRANSFER_RECIPIENT"
    AWAITING_TRANSFER_AMOUNT = "AWAITING_TRANSFER_AMOUNT"


def _state_key(telegram_id: int) -> str:
    return f"{FSM_KEY_PREFIX}{telegram_id}"


def _data_key(telegram_id: int) -> str:
    return f"{FSM_DATA_PREFIX}{telegram_id}"


async def get_state(telegram_id: int) -> UserState:
    """Retrieve the current conversation state for a user."""
    redis = await get_redis()
    raw = await redis.get(_state_key(telegram_id))
    if raw is None:
        return UserState.IDLE
    try:
        return UserState(raw)
    except ValueError:
        logger.warning("Unknown FSM state in Redis", telegram_id=telegram_id, raw=raw)
        return UserState.IDLE


async def set_state(telegram_id: int, state: UserState) -> None:
    """Set the conversation state for a user."""
    redis = await get_redis()
    await redis.setex(_state_key(telegram_id), FSM_TTL_SECONDS, state.value)
    logger.debug("FSM state set", telegram_id=telegram_id, state=state.value)


async def clear_state(telegram_id: int) -> None:
    """Reset user to IDLE and clear all context data."""
    redis = await get_redis()
    await redis.delete(_state_key(telegram_id), _data_key(telegram_id))
    logger.debug("FSM state cleared", telegram_id=telegram_id)


async def get_context(telegram_id: int) -> dict[str, Any]:
    """Retrieve context data (e.g., pending deposit amount)."""
    redis = await get_redis()
    raw = await redis.get(_data_key(telegram_id))
    if raw is None:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


async def set_context(telegram_id: int, data: dict[str, Any]) -> None:
    """Store context data alongside the FSM state."""
    redis = await get_redis()
    await redis.setex(_data_key(telegram_id), FSM_TTL_SECONDS, json.dumps(data))


async def update_context(telegram_id: int, **kwargs: Any) -> None:
    """Merge new key-value pairs into existing context data."""
    existing = await get_context(telegram_id)
    existing.update(kwargs)
    await set_context(telegram_id, existing)
