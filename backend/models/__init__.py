"""
Models package init.
"""
from backend.models.models import (
    Base,
    User,
    Deposit,
    Withdrawal,
    Transfer,
    UsedSMS,
    DepositStatus,
    WithdrawalStatus,
    TransferStatus,
    WalletTransaction,
    AuditLog,
    TransactionType,
    AuditAction,
)

from backend.models.bingo_models import (
    BingoGame,
    GamePlayer,
    Cartela,
    CalledNumber,
    GameEvent,
    GameStatus,
    PlayerStatus,
    GameEventType,
    WinPattern,
)

__all__ = [
    # Phase 1 models
    "Base",
    "User",
    "Deposit",
    "Withdrawal",
    "Transfer",
    "UsedSMS",
    "WalletTransaction",
    "AuditLog",
    "DepositStatus",
    "WithdrawalStatus",
    "TransferStatus",
    "TransactionType",
    "AuditAction",
    # Phase 2A Bingo models
    "BingoGame",
    "GamePlayer",
    "Cartela",
    "CalledNumber",
    "GameEvent",
    "GameStatus",
    "PlayerStatus",
    "GameEventType",
    "WinPattern",
]
