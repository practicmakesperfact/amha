"""
Bingo Game REST API routes.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.schemas.bingo_schemas import (
    GameCreateRequest,
    GameResponse,
    GameListResponse,
    PlayerResponse,
    CartelaResponse,
    GameStateResponse,
)
from backend.services.bingo_game_service import BingoGameService
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.cartela_repository import CartelaRepository
from backend.repositories.called_number_repository import CalledNumberRepository
from backend.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/bingo", tags=["Bingo"])


# Temporary auth helper - replace with actual Telegram auth
async def get_current_user_id(
    x_user_id: Optional[int] = Header(None, alias="X-User-Id")
) -> int:
    """Get current user ID from header (temporary - will use Telegram auth)."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return x_user_id


@router.get("/games", response_model=GameListResponse)
async def list_games(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List available games."""
    game_repo = BingoGameRepository(db)
    
    if status == "waiting":
        games = await game_repo.get_waiting_games(skip=skip, limit=limit)
    elif status == "active":
        games = await game_repo.get_active_games(skip=skip, limit=limit)
    else:
        games = await game_repo.get_all_games(skip=skip, limit=limit)
    
    # Get player count for each game
    player_repo = GamePlayerRepository(db)
    game_responses = []
    for game in games:
        player_count = await player_repo.get_active_players_count(game.id)
        game_dict = GameResponse.model_validate(game).model_dump()
        game_dict['player_count'] = player_count
        game_responses.append(GameResponse(**game_dict))
    
    return GameListResponse(
        games=game_responses,
        total=len(games),
        skip=skip,
        limit=limit,
    )


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get game details."""
    game_repo = BingoGameRepository(db)
    game = await game_repo.get_by_id(game_id)
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get player count
    player_repo = GamePlayerRepository(db)
    player_count = await player_repo.get_active_players_count(game_id)
    
    game_dict = GameResponse.model_validate(game).model_dump()
    game_dict['player_count'] = player_count
    
    return GameResponse(**game_dict)


@router.post("/games/{game_id}/join", response_model=PlayerResponse)
async def join_game(
    game_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Join a game."""
    try:
        async with db.begin():
            game_service = BingoGameService(db)
            player, cartela = await game_service.join_game(game_id, user_id)
            await db.commit()
            
        return PlayerResponse.model_validate(player)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error joining game", error=str(e), game_id=game_id, user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to join game")


@router.get("/games/{game_id}/state", response_model=GameStateResponse)
async def get_game_state(
    game_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get complete game state for a player."""
    game_repo = BingoGameRepository(db)
    player_repo = GamePlayerRepository(db)
    cartela_repo = CartelaRepository(db)
    called_number_repo = CalledNumberRepository(db)
    
    # Get game
    game = await game_repo.get_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get player count
    player_count = await player_repo.get_active_players_count(game_id)
    game_dict = GameResponse.model_validate(game).model_dump()
    game_dict['player_count'] = player_count
    game_response = GameResponse(**game_dict)
    
    # Get player (if joined)
    player = await player_repo.get_by_game_and_user(game_id, user_id)
    player_response = PlayerResponse.model_validate(player) if player else None
    
    # Get cartela (if player joined)
    cartela = None
    if player:
        cartela = await cartela_repo.get_by_id(player.cartela_id)
    cartela_response = CartelaResponse.model_validate(cartela) if cartela else None
    
    # Get called numbers
    called_numbers_list = await called_number_repo.get_called_numbers_by_game(game_id)
    called_numbers = [cn.number for cn in called_numbers_list]
    
    # Get last called number
    last_called = await called_number_repo.get_latest_called_number(game_id)
    
    return GameStateResponse(
        game=game_response,
        player=player_response,
        cartela=cartela_response,
        called_numbers=called_numbers,
        last_called=last_called,
    )


@router.get("/games/{game_id}/cartela", response_model=CartelaResponse)
async def get_my_cartela(
    game_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get player's cartela for a game."""
    cartela_repo = CartelaRepository(db)
    cartela = await cartela_repo.get_by_game_and_user(game_id, user_id)
    
    if not cartela:
        raise HTTPException(status_code=404, detail="Cartela not found")
    
    return CartelaResponse.model_validate(cartela)


@router.get("/me/games", response_model=GameListResponse)
async def get_my_games(
    skip: int = 0,
    limit: int = 100,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get all games the current user has joined."""
    player_repo = GamePlayerRepository(db)
    players = await player_repo.get_players_by_user(user_id, skip=skip, limit=limit)
    
    # Get games for these players
    game_repo = BingoGameRepository(db)
    games = []
    for player in players:
        game = await game_repo.get_by_id(player.game_id)
        if game:
            player_count = await player_repo.get_active_players_count(game.id)
            game_dict = GameResponse.model_validate(game).model_dump()
            game_dict['player_count'] = player_count
            games.append(GameResponse(**game_dict))
    
    return GameListResponse(
        games=games,
        total=len(games),
        skip=skip,
        limit=limit,
    )


@router.get("/me/stats")
async def get_my_stats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get player statistics."""
    from backend.services.player_stats_service import PlayerStatsService
    
    stats_service = PlayerStatsService(db)
    stats = await stats_service.get_player_stats(user_id)
    
    return stats
