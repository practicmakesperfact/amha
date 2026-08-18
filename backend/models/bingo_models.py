"""
Bingo game models for Phase 2A.
Extends existing User and financial models from Phase 1.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


# ── Enums ────────────────────────────────────────────────────────────────────


class GameStatus(str, enum.Enum):
    """Game lifecycle states."""
    WAITING = "WAITING"
    STARTING = "STARTING"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"


class PlayerStatus(str, enum.Enum):
    """Player participation status."""
    JOINED = "JOINED"
    ACTIVE = "ACTIVE"
    DISCONNECTED = "DISCONNECTED"
    LEFT = "LEFT"
    WINNER = "WINNER"


class GameEventType(str, enum.Enum):
    """Types of game events."""
    GAME_CREATED = "GAME_CREATED"
    PLAYER_JOINED = "PLAYER_JOINED"
    PLAYER_LEFT = "PLAYER_LEFT"
    GAME_STARTING = "GAME_STARTING"
    GAME_STARTED = "GAME_STARTED"
    NUMBER_CALLED = "NUMBER_CALLED"
    GAME_PAUSED = "GAME_PAUSED"
    GAME_RESUMED = "GAME_RESUMED"
    WINNER_DECLARED = "WINNER_DECLARED"
    PRIZE_PAID = "PRIZE_PAID"
    GAME_FINISHED = "GAME_FINISHED"
    GAME_CANCELLED = "GAME_CANCELLED"
    REFUND_ISSUED = "REFUND_ISSUED"


class WinPattern(str, enum.Enum):
    """Bingo winning patterns."""
    ROW = "ROW"
    COLUMN = "COLUMN"
    DIAGONAL = "DIAGONAL"
    FULL_CARD = "FULL_CARD"


# ── BingoGame ────────────────────────────────────────────────────────────────


class BingoGame(Base):
    """Main game entity."""
    __tablename__ = "bingo_games"
    __table_args__ = (
        CheckConstraint("entry_fee >= 0", name="ck_bingo_game_entry_fee_positive"),
        CheckConstraint("prize_pool >= 0", name="ck_bingo_game_prize_pool_positive"),
        CheckConstraint("max_players > 0", name="ck_bingo_game_max_players_positive"),
        CheckConstraint("min_players > 0", name="ck_bingo_game_min_players_positive"),
        Index("idx_bingo_game_status", "status"),
        Index("idx_bingo_game_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    
    # Game configuration
    entry_fee: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    prize_pool: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    min_players: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    
    # Game state
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus), nullable=False, default=GameStatus.WAITING)
    current_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    numbers_called_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Prize configuration (JSON: {first: 60, second: 30, third: 10})
    prize_distribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Admin info
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Relationships
    players: Mapped[list[GamePlayer]] = relationship("GamePlayer", back_populates="game", cascade="all, delete-orphan")
    cartelas: Mapped[list[Cartela]] = relationship("Cartela", back_populates="game", cascade="all, delete-orphan")
    called_numbers: Mapped[list[CalledNumber]] = relationship("CalledNumber", back_populates="game", cascade="all, delete-orphan")
    events: Mapped[list[GameEvent]] = relationship("GameEvent", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BingoGame id={self.id} number={self.game_number} status={self.status}>"


# ── GamePlayer ───────────────────────────────────────────────────────────────


class GamePlayer(Base):
    """Player participation in a game."""
    __tablename__ = "game_players"
    __table_args__ = (
        UniqueConstraint("game_id", "user_id", name="uq_game_player"),
        CheckConstraint("entry_fee >= 0", name="ck_game_player_entry_fee_positive"),
        CheckConstraint("prize_amount >= 0", name="ck_game_player_prize_positive"),
        Index("idx_game_player_game", "game_id"),
        Index("idx_game_player_user", "user_id"),
        Index("idx_game_player_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("bingo_games.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cartela_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cartelas.id", ondelete="SET NULL"), nullable=True)
    
    # Financial
    entry_fee: Mapped[float] = mapped_column(Float, nullable=False)
    prize_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Status
    status: Mapped[PlayerStatus] = mapped_column(Enum(PlayerStatus), nullable=False, default=PlayerStatus.JOINED)
    is_winner: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    winning_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    win_pattern: Mapped[Optional[WinPattern]] = mapped_column(Enum(WinPattern), nullable=True)
    
    # Game state (JSON array of marked numbers)
    marked_numbers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    game: Mapped[BingoGame] = relationship("BingoGame", back_populates="players")
    from backend.models.models import User
    user: Mapped[User] = relationship("User")
    cartela: Mapped[Optional[Cartela]] = relationship("Cartela", foreign_keys=[cartela_id])

    def __repr__(self) -> str:
        return f"<GamePlayer id={self.id} game={self.game_id} user={self.user_id} status={self.status}>"


# ── Cartela ──────────────────────────────────────────────────────────────────


class Cartela(Base):
    """Bingo cartela (card) - 5x5 grid."""
    __tablename__ = "cartelas"
    __table_args__ = (
        UniqueConstraint("game_id", "user_id", name="uq_cartela_game_user"),
        Index("idx_cartela_game", "game_id"),
        Index("idx_cartela_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("bingo_games.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Cartela data (JSON array: 5x5 grid with FREE center)
    # Example: [[5,12,3,14,8], [19,22,28,17,30], [34,39,0,41,36], ...]
    # 0 represents FREE
    numbers: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Cartela ID for display
    cartela_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    game: Mapped[BingoGame] = relationship("BingoGame", back_populates="cartelas")
    from backend.models.models import User
    user: Mapped[User] = relationship("User")

    def __repr__(self) -> str:
        return f"<Cartela id={self.id} game={self.game_id} user={self.user_id} number={self.cartela_number}>"


# ── CalledNumber ─────────────────────────────────────────────────────────────


class CalledNumber(Base):
    """History of called numbers in a game."""
    __tablename__ = "called_numbers"
    __table_args__ = (
        UniqueConstraint("game_id", "number", name="uq_called_number_game"),
        CheckConstraint("number >= 1 AND number <= 75", name="ck_called_number_range"),
        CheckConstraint("sequence > 0", name="ck_called_number_sequence_positive"),
        Index("idx_called_number_game", "game_id"),
        Index("idx_called_number_sequence", "game_id", "sequence"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("bingo_games.id", ondelete="CASCADE"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    column_letter: Mapped[str] = mapped_column(String(1), nullable=False)  # B, I, N, G, O
    called_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    game: Mapped[BingoGame] = relationship("BingoGame", back_populates="called_numbers")

    def __repr__(self) -> str:
        return f"<CalledNumber id={self.id} game={self.game_id} {self.column_letter}{self.number} seq={self.sequence}>"


# ── GameEvent ────────────────────────────────────────────────────────────────


class GameEvent(Base):
    """Event log for game lifecycle."""
    __tablename__ = "game_events"
    __table_args__ = (
        Index("idx_game_event_game", "game_id"),
        Index("idx_game_event_type", "event_type"),
        Index("idx_game_event_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("bingo_games.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[GameEventType] = mapped_column(Enum(GameEventType), nullable=False)
    
    # Optional references
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    player_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Event data (JSON)
    event_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    game: Mapped[BingoGame] = relationship("BingoGame", back_populates="events")

    def __repr__(self) -> str:
        return f"<GameEvent id={self.id} game={self.game_id} type={self.event_type}>"
