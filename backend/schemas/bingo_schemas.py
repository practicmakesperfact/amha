"""
Pydantic schemas for Bingo game API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from backend.models.bingo_models import GameStatus, PlayerStatus, WinPattern


# ── Game Schemas ──────────────────────────────────────────────────────────


class GameCreateRequest(BaseModel):
    """Request to create a new game."""
    entry_fee: float = Field(..., gt=0, description="Entry fee in ETB")
    max_players: Optional[int] = Field(None, gt=0, description="Maximum players")
    min_players: Optional[int] = Field(None, gt=0, description="Minimum players")
    prize_distribution: Optional[dict] = Field(None, description="Prize distribution config")


class GameResponse(BaseModel):
    """Game information response."""
    id: int
    game_number: str
    status: GameStatus
    entry_fee: float
    prize_pool: float
    max_players: int
    min_players: int
    current_number: Optional[int]
    numbers_called_count: int
    player_count: Optional[int] = None
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    """List of games response."""
    games: List[GameResponse]
    total: int
    skip: int
    limit: int


# ── Player Schemas ────────────────────────────────────────────────────────


class PlayerJoinRequest(BaseModel):
    """Request to join a game."""
    pass  # Game ID comes from path, user ID from auth


class PlayerResponse(BaseModel):
    """Player information response."""
    id: int
    game_id: int
    user_id: int
    cartela_id: Optional[int]
    entry_fee: float
    prize_amount: float
    status: PlayerStatus
    is_winner: bool
    winning_position: Optional[int]
    win_pattern: Optional[WinPattern]
    joined_at: datetime
    left_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Cartela Schemas ───────────────────────────────────────────────────────


class CartelaResponse(BaseModel):
    """Cartela information response."""
    id: int
    game_id: int
    user_id: int
    numbers: List[List[int]]  # 5x5 grid
    cartela_number: str
    created_at: datetime

    @field_validator('numbers', mode='before')
    @classmethod
    def parse_numbers(cls, v):
        """Parse JSON string to nested list."""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    class Config:
        from_attributes = True


# ── Game State Schemas ────────────────────────────────────────────────────


class CalledNumberResponse(BaseModel):
    """Called number information."""
    number: int
    column_letter: str
    sequence: int
    called_at: datetime

    class Config:
        from_attributes = True


class GameStateResponse(BaseModel):
    """Complete game state for player."""
    game: GameResponse
    player: Optional[PlayerResponse]
    cartela: Optional[CartelaResponse]
    called_numbers: List[int]
    last_called: Optional[CalledNumberResponse]


# ── WebSocket Event Schemas ───────────────────────────────────────────────


class WSEventBase(BaseModel):
    """Base WebSocket event."""
    event: str
    game_id: int
    timestamp: datetime


class WSNumberCalledEvent(WSEventBase):
    """Number called WebSocket event."""
    event: str = "NUMBER_CALLED"
    number: int
    column_letter: str
    sequence: int


class WSPlayerJoinedEvent(WSEventBase):
    """Player joined WebSocket event."""
    event: str = "PLAYER_JOINED"
    user_id: int
    player_count: int


class WSWinnerDeclaredEvent(WSEventBase):
    """Winner declared WebSocket event."""
    event: str = "WINNER_DECLARED"
    user_id: int
    winning_position: int
    win_pattern: WinPattern
    prize_amount: float


class WSGameFinishedEvent(WSEventBase):
    """Game finished WebSocket event."""
    event: str = "GAME_FINISHED"
    winners: List[dict]


class WSErrorEvent(WSEventBase):
    """Error WebSocket event."""
    event: str = "ERROR"
    message: str


# ── Statistics Schemas ────────────────────────────────────────────────────


class PlayerStatsResponse(BaseModel):
    """Player statistics response."""
    user_id: int
    games_played: int
    games_won: int
    win_rate: float
    total_entry_fees: float
    total_winnings: float
    net_profit: float
