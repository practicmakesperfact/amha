"""
Admin Bingo Game API routes.
Extends existing admin authentication.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.schemas.bingo_schemas import (
    GameCreateRequest,
    GameResponse,
    GameListResponse,
    PlayerResponse,
)
from backend.models.bingo_models import GameStatus
from backend.services.bingo_game_service import BingoGameService
from backend.services.number_caller_service import NumberCallerService
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.game_event_repository import GameEventRepository
from backend.repositories.user_repository import UserRepository
from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/bingo", tags=["Admin Bingo"])


# Reuse existing admin authentication
async def verify_admin(
    x_admin_id: Optional[int] = Header(None, alias="X-Admin-Id"),
    db: AsyncSession = Depends(get_db),
) -> int:
    """Verify admin authentication using existing pattern."""
    if not x_admin_id:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    
    # Verify admin exists and has admin flag
    user_repo = UserRepository(db)
    admin = await user_repo.get_by_id(x_admin_id)
    
    if not admin or not admin.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return x_admin_id


@router.post("/games", response_model=GameResponse)
async def create_game(
    request: GameCreateRequest,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new Bingo game."""
    try:
        async with db.begin():
            game_service = BingoGameService(db)
            game = await game_service.create_game(
                entry_fee=request.entry_fee,
                max_players=request.max_players,
                min_players=request.min_players,
                created_by=admin_id,
                prize_distribution=request.prize_distribution,
            )
            await db.commit()
        
        player_repo = GamePlayerRepository(db)
        player_count = await player_repo.get_active_players_count(game.id)
        
        game_dict = GameResponse.model_validate(game).model_dump()
        game_dict['player_count'] = player_count
        
        return GameResponse(**game_dict)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error creating game", error=str(e), admin_id=admin_id)
        raise HTTPException(status_code=500, detail="Failed to create game")


@router.get("/games", response_model=GameListResponse)
async def list_all_games(
    skip: int = 0,
    limit: int = 100,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all games (admin view)."""
    game_repo = BingoGameRepository(db)
    games = await game_repo.get_all_games(skip=skip, limit=limit)
    
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
async def get_game_details(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed game information."""
    game_repo = BingoGameRepository(db)
    game = await game_repo.get_by_id(game_id)
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    player_repo = GamePlayerRepository(db)
    player_count = await player_repo.get_active_players_count(game_id)
    
    game_dict = GameResponse.model_validate(game).model_dump()
    game_dict['player_count'] = player_count
    
    return GameResponse(**game_dict)


@router.post("/games/{game_id}/start")
async def start_game(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Start a game."""
    try:
        async with db.begin():
            from backend.services.game_engine_service import GameEngineService
            engine = GameEngineService(db)
            game = await engine.start_game(game_id)
            await db.commit()
        
        logger.info("Game started", game_id=game_id, admin_id=admin_id)
        return {"message": "Game started", "game_id": game_id, "status": game.status}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error starting game", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to start game")


@router.post("/games/{game_id}/call-number")
async def call_number(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Manually call next number and check for winners."""
    try:
        async with db.begin():
            from backend.services.game_engine_service import GameEngineService
            engine = GameEngineService(db)
            winners = await engine.call_number_and_check_winners(game_id)
            await db.commit()
        
        result = {
            "message": "Number called successfully",
            "winners": [],
        }
        
        if winners:
            result["winners"] = [
                {
                    "user_id": w.user_id,
                    "winning_position": w.winning_position,
                    "win_pattern": w.win_pattern.value if w.win_pattern else None,
                    "prize_amount": w.prize_amount,
                }
                for w in winners
            ]
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error calling number", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to call number")


@router.get("/games/{game_id}/players", response_model=List[PlayerResponse])
async def get_game_players(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all players in a game."""
    player_repo = GamePlayerRepository(db)
    players = await player_repo.get_players_by_game(game_id)
    
    return [PlayerResponse.model_validate(p) for p in players]


@router.post("/games/{game_id}/pause")
async def pause_game(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Pause a playing game."""
    try:
        async with db.begin():
            from backend.services.game_engine_service import GameEngineService
            engine = GameEngineService(db)
            game = await engine.pause_game(game_id)
            await db.commit()
        
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        logger.info("Game paused", game_id=game_id, admin_id=admin_id)
        return {"message": "Game paused", "game_id": game_id, "status": game.status}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error pausing game", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to pause game")


@router.post("/games/{game_id}/resume")
async def resume_game(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused game."""
    try:
        async with db.begin():
            from backend.services.game_engine_service import GameEngineService
            engine = GameEngineService(db)
            game = await engine.resume_game(game_id)
            await db.commit()
        
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        logger.info("Game resumed", game_id=game_id, admin_id=admin_id)
        return {"message": "Game resumed", "game_id": game_id, "status": game.status}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error resuming game", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to resume game")


@router.post("/games/{game_id}/finish")
async def finish_game(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Finish a game."""
    try:
        async with db.begin():
            from backend.services.game_engine_service import GameEngineService
            engine = GameEngineService(db)
            game = await engine.finish_game(game_id)
            await db.commit()
        
        logger.info("Game finished", game_id=game_id, admin_id=admin_id)
        return {"message": "Game finished", "game_id": game_id, "status": game.status}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error finishing game", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to finish game")


@router.get("/games/{game_id}/players", response_model=List[PlayerResponse])
async def get_game_players(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all players in a game."""
    player_repo = GamePlayerRepository(db)
    players = await player_repo.get_players_by_game(game_id)
    
    return [PlayerResponse.model_validate(p) for p in players]


@router.post("/games/{game_id}/cancel")
async def cancel_game(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a game and refund players."""
    try:
        async with db.begin():
            game_repo = BingoGameRepository(db)
            player_repo = GamePlayerRepository(db)
            user_repo = UserRepository(db)
            
            game = await game_repo.get_by_id(game_id)
            if not game:
                raise HTTPException(status_code=404, detail="Game not found")
            
            if game.status == GameStatus.FINISHED:
                raise HTTPException(status_code=400, detail="Cannot cancel finished game")
            
            # Get all players
            players = await player_repo.get_players_by_game(game_id)
            
            # Refund each player
            from backend.models.models import TransactionType
            for player in players:
                if player.entry_fee > 0:
                    # Credit refund
                    from sqlalchemy import select
                    result = await db.execute(
                        select(User).where(User.id == player.user_id).with_for_update()
                    )
                    user = result.scalar_one_or_none()
                    
                    if user:
                        balance_before = user.main_wallet
                        user.main_wallet = round(user.main_wallet + player.entry_fee, 2)
                        balance_after = user.main_wallet
                        
                        # Record wallet transaction
                        try:
                            from backend.repositories.wallet_transaction_repository import WalletTransactionRepository
                            wallet_tx_repo = WalletTransactionRepository(db)
                            await wallet_tx_repo.create_transaction(
                                user_id=user.id,
                                transaction_type=TransactionType.ADMIN_CREDIT,
                                amount=player.entry_fee,
                                balance_before=balance_before,
                                balance_after=balance_after,
                                description=f"Refund - Game {game.game_number} cancelled",
                            )
                        except Exception as e:
                            logger.warning("Could not record wallet transaction", error=str(e))
            
            # Update game status
            game = await game_repo.update_status(game_id, GameStatus.CANCELLED)
            game.finished_at = db.scalar("SELECT NOW()")
            
            # Log event
            from backend.models.bingo_models import GameEvent, GameEventType
            event = GameEvent(
                game_id=game_id,
                event_type=GameEventType.GAME_CANCELLED,
                description=f"Game cancelled and refunded by admin {admin_id}",
            )
            db.add(event)
            
            await db.commit()
        
        logger.info("Game cancelled", game_id=game_id, admin_id=admin_id, players_refunded=len(players))
        return {
            "message": "Game cancelled and players refunded",
            "game_id": game_id,
            "players_refunded": len(players),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error cancelling game", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to cancel game")



@router.post("/games/{game_id}/pause")
async def pause_game(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Pause a running game."""
    try:
        async with db.begin():
            from backend.services.bingo_game_service import BingoGameService
            game_service = BingoGameService(db)
            game = await game_service.pause_game(game_id)
            await db.commit()
        
        return {"message": "Game paused", "game_id": game_id, "status": game.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error pausing game", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to pause game")


@router.post("/games/{game_id}/resume")
async def resume_game(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused game."""
    try:
        async with db.begin():
            from backend.services.bingo_game_service import BingoGameService
            game_service = BingoGameService(db)
            game = await game_service.resume_game(game_id)
            await db.commit()
        
        return {"message": "Game resumed", "game_id": game_id, "status": game.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error resuming game", error=str(e), game_id=game_id)
        raise HTTPException(status_code=500, detail="Failed to resume game")


@router.get("/games/{game_id}/events")
async def get_game_events(
    game_id: int,
    skip: int = 0,
    limit: int = 100,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get game events history."""
    event_repo = GameEventRepository(db)
    events = await event_repo.get_events_by_game(game_id, skip=skip, limit=limit)
    
    return {
        "game_id": game_id,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "user_id": e.user_id,
                "player_id": e.player_id,
                "description": e.description,
                "created_at": e.created_at,
            }
            for e in events
        ],
        "total": len(events),
    }


@router.get("/games/{game_id}/winners")
async def get_game_winners(
    game_id: int,
    admin_id: int = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all winners for a game."""
    player_repo = GamePlayerRepository(db)
    winners = await player_repo.get_winners_by_game(game_id)
    
    return {
        "game_id": game_id,
        "winners": [PlayerResponse.model_validate(w) for w in winners],
        "total_winners": len(winners),
    }
