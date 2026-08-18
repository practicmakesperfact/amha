"""
WebSocket routes for real-time Bingo game updates.
"""

import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from redis.asyncio import Redis

from backend.core.redis import get_redis
from backend.services.game_state_service import GameStateService
from backend.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for games."""

    def __init__(self):
        # game_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: int, user_id: int):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        
        if game_id not in self.active_connections:
            self.active_connections[game_id] = set()
        
        self.active_connections[game_id].add(websocket)
        
        logger.info("WebSocket connected", game_id=game_id, user_id=user_id)

    def disconnect(self, websocket: WebSocket, game_id: int):
        """Remove a WebSocket connection."""
        if game_id in self.active_connections:
            self.active_connections[game_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))

    async def broadcast_to_game(self, message: dict, game_id: int):
        """Broadcast message to all clients in a game."""
        if game_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[game_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning("Failed to send to connection", error=str(e))
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections[game_id].discard(connection)


manager = ConnectionManager()


async def subscribe_to_game_events(game_id: int):
    """
    Subscribe to Redis Pub/Sub for game events and broadcast to WebSocket clients.
    """
    redis = await get_redis()
    state_service = GameStateService()
    channel_name = state_service._events_channel(game_id)
    
    try:
        # For in-memory Redis mock, skip Pub/Sub
        if hasattr(redis, '_data'):
            logger.info("In-memory Redis - Pub/Sub not available")
            return
        
        # Real Redis Pub/Sub
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel_name)
        
        logger.info("Subscribed to game events", game_id=game_id, channel=channel_name)
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    event_data = json.loads(message['data'])
                    await manager.broadcast_to_game(event_data, game_id)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in Pub/Sub message")
    
    except Exception as e:
        logger.error("Error in Pub/Sub subscription", error=str(e), game_id=game_id)


@router.websocket("/ws/bingo/{game_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    game_id: int,
    user_id: int = Query(...),  # Temporary - replace with proper auth
):
    """
    WebSocket endpoint for real-time game updates.
    
    Query params:
        user_id: User ID (temporary auth - replace with Telegram auth token)
    """
    await manager.connect(websocket, game_id, user_id)
    
    # Send initial game state
    state_service = GameStateService()
    game_state = await state_service.get_game_state(game_id)
    
    if game_state:
        await manager.send_personal_message(
            {
                "event": "GAME_STATE",
                "game_id": game_id,
                **game_state,
            },
            websocket,
        )
    
    # Start Pub/Sub listener (in background)
    # Note: For production, use a dedicated worker process
    # For now, each connection creates its own listener (not ideal but functional)
    
    try:
        # Keep connection alive and handle client messages
        while True:
            try:
                # Receive messages from client (e.g., heartbeat, winner claims)
                data = await websocket.receive_json()
                
                # Handle different message types
                if data.get("type") == "PING":
                    await manager.send_personal_message(
                        {"type": "PONG", "timestamp": data.get("timestamp")},
                        websocket,
                    )
                
                # Add more message handlers as needed
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("Error receiving WebSocket message", error=str(e))
                break
    
    finally:
        manager.disconnect(websocket, game_id)
        logger.info("WebSocket disconnected", game_id=game_id, user_id=user_id)
