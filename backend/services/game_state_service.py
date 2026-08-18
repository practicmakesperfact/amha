"""
Game State Service — Redis-based real-time game state management.
"""

import json
from typing import Optional, Set, Dict, Any
from redis.asyncio import Redis

from backend.core.redis import get_redis
from backend.core.logging import get_logger

logger = get_logger(__name__)


class GameStateService:
    """Manage real-time game state in Redis."""

    def __init__(self):
        self.redis: Optional[Redis] = None

    async def _get_redis(self) -> Redis:
        """Get Redis connection."""
        if self.redis is None:
            self.redis = await get_redis()
        return self.redis

    def _game_key(self, game_id: int) -> str:
        """Get Redis key for game state."""
        return f"bingo:game:{game_id}"

    def _players_key(self, game_id: int) -> str:
        """Get Redis key for player count."""
        return f"bingo:game:{game_id}:players"

    def _called_key(self, game_id: int) -> str:
        """Get Redis key for called numbers set."""
        return f"bingo:game:{game_id}:called"

    def _events_channel(self, game_id: int) -> str:
        """Get Redis Pub/Sub channel for game events."""
        return f"bingo:game:{game_id}:events"

    async def set_game_state(
        self,
        game_id: int,
        status: str,
        current_number: Optional[int] = None,
        numbers_called_count: int = 0,
        player_count: int = 0,
        prize_pool: float = 0.0,
    ) -> bool:
        """
        Store game state in Redis.
        
        Args:
            game_id: Game ID
            status: Game status
            current_number: Last called number
            numbers_called_count: Count of called numbers
            player_count: Active player count
            prize_pool: Current prize pool
            
        Returns:
            True if successful
        """
        try:
            redis = await self._get_redis()
            key = self._game_key(game_id)
            
            state = {
                "game_id": game_id,
                "status": status,
                "current_number": current_number,
                "numbers_called_count": numbers_called_count,
                "player_count": player_count,
                "prize_pool": prize_pool,
                "updated_at": str(datetime.utcnow()),
            }
            
            # Store as JSON with 24 hour expiry
            await redis.setex(key, 86400, json.dumps(state))
            
            logger.debug("Game state updated in Redis", game_id=game_id, status=status)
            return True
        
        except Exception as e:
            logger.error("Failed to set game state in Redis", error=str(e), game_id=game_id)
            return False

    async def get_game_state(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Get game state from Redis.
        
        Args:
            game_id: Game ID
            
        Returns:
            Game state dict or None
        """
        try:
            redis = await self._get_redis()
            key = self._game_key(game_id)
            
            data = await redis.get(key)
            if data:
                return json.loads(data)
            
            return None
        
        except Exception as e:
            logger.error("Failed to get game state from Redis", error=str(e), game_id=game_id)
            return None

    async def add_called_number(self, game_id: int, number: int) -> bool:
        """
        Add a called number to the set.
        
        Args:
            game_id: Game ID
            number: Called number
            
        Returns:
            True if successful
        """
        try:
            redis = await self._get_redis()
            key = self._called_key(game_id)
            
            # Add to set with 24 hour expiry
            await redis.sadd(key, number)
            await redis.expire(key, 86400)
            
            return True
        
        except Exception as e:
            logger.error("Failed to add called number to Redis", error=str(e), game_id=game_id)
            return False

    async def get_called_numbers(self, game_id: int) -> Set[int]:
        """
        Get set of all called numbers from Redis.
        
        Args:
            game_id: Game ID
            
        Returns:
            Set of called numbers
        """
        try:
            redis = await self._get_redis()
            key = self._called_key(game_id)
            
            members = await redis.smembers(key)
            return {int(n) for n in members}
        
        except Exception as e:
            logger.error("Failed to get called numbers from Redis", error=str(e), game_id=game_id)
            return set()

    async def publish_event(
        self,
        game_id: int,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> bool:
        """
        Publish an event to the game's Pub/Sub channel.
        
        Args:
            game_id: Game ID
            event_type: Event type (e.g., "NUMBER_CALLED")
            event_data: Event payload
            
        Returns:
            True if successful
        """
        try:
            redis = await self._get_redis()
            channel = self._events_channel(game_id)
            
            message = {
                "event": event_type,
                "game_id": game_id,
                "timestamp": str(datetime.utcnow()),
                **event_data,
            }
            
            await redis.publish(channel, json.dumps(message))
            
            logger.debug("Event published", game_id=game_id, event=event_type)
            return True
        
        except Exception as e:
            logger.error("Failed to publish event", error=str(e), game_id=game_id, event=event_type)
            return False

    async def increment_player_count(self, game_id: int) -> int:
        """
        Increment player count for a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            New player count
        """
        try:
            redis = await self._get_redis()
            key = self._players_key(game_id)
            
            count = await redis.incr(key)
            await redis.expire(key, 86400)
            
            return count
        
        except Exception as e:
            logger.error("Failed to increment player count", error=str(e), game_id=game_id)
            return 0

    async def get_player_count(self, game_id: int) -> int:
        """
        Get player count from Redis.
        
        Args:
            game_id: Game ID
            
        Returns:
            Player count
        """
        try:
            redis = await self._get_redis()
            key = self._players_key(game_id)
            
            count = await redis.get(key)
            return int(count) if count else 0
        
        except Exception as e:
            logger.error("Failed to get player count", error=str(e), game_id=game_id)
            return 0

    async def delete_game_state(self, game_id: int) -> bool:
        """
        Delete all Redis state for a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            True if successful
        """
        try:
            redis = await self._get_redis()
            
            keys = [
                self._game_key(game_id),
                self._players_key(game_id),
                self._called_key(game_id),
            ]
            
            await redis.delete(*keys)
            
            logger.info("Game state deleted from Redis", game_id=game_id)
            return True
        
        except Exception as e:
            logger.error("Failed to delete game state", error=str(e), game_id=game_id)
            return False


# Import datetime here to avoid circular import at module level
from datetime import datetime
