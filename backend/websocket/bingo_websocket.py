"""
WebSocket endpoint for real-time Bingo game events.
"""

import json
import asyncio
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.called_number_repository import CalledNumberRepository
from backend.services.redis_game_state_service import RedisGameStateService
from backend.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for Bingo games."""

    def __init__(self):
        # game_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: int):
        """Accept connection and add to game room."""
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = set()
        self.active_connections[game_id].add(websocket)
        logger.info("WebSocket connected", game_id=game_id, total=len(self.active_connections[game_id]))

    def disconnect(self, websocket: WebSocket, game_id: int):
        """Remove connection from game room."""
        if game_id in self.active_connections:
            self.active_connections[game_id].discard(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
        logger.info("WebSocket disconnected", game_id=game_id)

    async def broadcast_to_game(self, game_id: int, message: dict):
        """Broadcast message to all connections in a game room."""
        if game_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[game_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning("Failed to send to WebSocket", error=str(e))
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn, game_id)

    async def send_to_client(self, websocket: WebSocket, message: dict):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning("Failed to send to client", error=str(e))


manager = ConnectionManager()


@router.websocket("/ws/bingo/{game_id}")
async def bingo_websocket(
    websocket: WebSocket,
    game_id: int,
    user_id: int = Query(..., description="User ID for authentication"),
):
    """
    WebSocket endpoint for real-time Bingo game events.
    
    Query Parameters:
        user_id: Telegram user ID for authentication
    
    Events sent to client:
        - GAME_STATE: Initial synchronized state
        - PLAYER_JOINED: New player joined
        - PLAYER_COUNT_UPDATED: Player count changed
        - NUMBER_CALLED: New number called
        - WINNER_DECLARED: Winner announced
        - GAME_FINISHED: Game ended
        - ERROR: Error message
    """
    await manager.connect(websocket, game_id)

    try:
        # Verify game exists and get initial state
        async for db in get_db():
            game_repo = BingoGameRepository(db)
            player_repo = GamePlayerRepository(db)
            called_number_repo = CalledNumberRepository(db)
            redis_state = RedisGameStateService()

            game = await game_repo.get_by_id(game_id)
            if not game:
                await manager.send_to_client(
                    websocket,
                    {
                        "event": "ERROR",
                        "message": "Game not found",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                await websocket.close()
                return

            # Verify user is a player in the game
            player = await player_repo.get_by_game_and_user(game_id, user_id)
            if not player:
                await manager.send_to_client(
                    websocket,
                    {
                        "event": "ERROR",
                        "message": "You are not a player in this game",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                await websocket.close()
                return

            # Send initial game state
            called_numbers = await called_number_repo.get_called_numbers_by_game(game_id)
            player_count = await player_repo.get_active_players_count(game_id)

            await manager.send_to_client(
                websocket,
                {
                    "event": "GAME_STATE",
                    "game_id": game_id,
                    "status": game.status.value,
                    "current_number": game.current_number,
                    "numbers_called_count": game.numbers_called_count,
                    "called_numbers": [cn.number for cn in called_numbers],
                    "player_count": player_count,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            logger.info(
                "Initial game state sent",
                game_id=game_id,
                user_id=user_id,
                player_id=player.id,
            )

            break  # Exit async for loop after first iteration

        # Keep connection alive and handle heartbeat
        while True:
            try:
                # Receive messages from client (heartbeat/ping)
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                
                # Handle ping/pong
                if data.get("type") == "ping":
                    await manager.send_to_client(
                        websocket,
                        {
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

            except asyncio.TimeoutError:
                # Send keepalive ping
                try:
                    await manager.send_to_client(
                        websocket,
                        {
                            "type": "keepalive",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )
                except:
                    break

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("WebSocket error", error=str(e), game_id=game_id)
                break

    except Exception as e:
        logger.error("WebSocket connection error", error=str(e), game_id=game_id)

    finally:
        manager.disconnect(websocket, game_id)


async def broadcast_number_called(
    game_id: int, number: int, column_letter: str, sequence: int
):
    """Broadcast number called event to all clients in game."""
    await manager.broadcast_to_game(
        game_id,
        {
            "event": "NUMBER_CALLED",
            "game_id": game_id,
            "number": number,
            "column_letter": column_letter,
            "sequence": sequence,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def broadcast_player_joined(game_id: int, user_id: int, player_count: int):
    """Broadcast player joined event."""
    await manager.broadcast_to_game(
        game_id,
        {
            "event": "PLAYER_JOINED",
            "game_id": game_id,
            "user_id": user_id,
            "player_count": player_count,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def broadcast_winner_declared(
    game_id: int,
    user_id: int,
    winning_position: int,
    win_pattern: str,
    prize_amount: float,
):
    """Broadcast winner declared event."""
    await manager.broadcast_to_game(
        game_id,
        {
            "event": "WINNER_DECLARED",
            "game_id": game_id,
            "user_id": user_id,
            "winning_position": winning_position,
            "win_pattern": win_pattern,
            "prize_amount": prize_amount,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def broadcast_game_finished(game_id: int):
    """Broadcast game finished event."""
    await manager.broadcast_to_game(
        game_id,
        {
            "event": "GAME_FINISHED",
            "game_id": game_id,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
