"""
Redis Game State Service — manages real-time game state in Redis.
"""

import json
from typing import Optional, List, Set
from redis.asyncio import Redis

from backend.core.redis import get_redis
from backend.core.logging import get_logger

logger = get_logger(__name__)


class RedisGameStateService:
    """Manages game state in Redis for real-time access."""

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

    def _called_numbers_key(self, game_id: int) -> str:
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
        ttl: int = 3600,
    ) -> bool:
        """
        Store game state in Redis.
        
        Args:
            game_id: Game ID
            status: Game status
            current_number: Last called number
            numbers_called_count: Count of called numbers
            player_count: Active player count
            ttl: TTL in seconds (default 1 hour)
            
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
            }
            
            await redis.setex(key, ttl, json.dumps(state))
            logger.debug("Game state saved to Redis", game_id=game_id)
            return True
        
        except Exception as e:
            logger.warning("Failed to set game state in Redis", error=str(e), game_id=game_id)
            return False

    async def get_game_state(self, game_id: int) -> Optional[dict]:
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
            logger.warning("Failed to get game state from Redis", error=str(e), game_id=game_id)
            return None

    async def add_called_number(self, game_id: int, number: int, ttl: int = 3600) -> bool:
        """
        Add a called number to Redis set.
        
        Args:
            game_id: Game ID
            number: Called number
            ttl: TTL in seconds
            
        Returns:
            True if successful
        """
        try:
            redis = await self._get_redis()
            key = self._called_numbers_key(game_id)
            
            # Use sorted set with number as score for ordering
            await redis.zadd(key, {str(number): number})
            await redis.expire(key, ttl)
            
            return True
        
        except Exception as e:
            logger.warning("Failed to add called number to Redis", error=str(e), game_id=game_id)
            return False

    async def get_called_numbers(self, game_id: int) -> Set[int]:
        """
        Get all called numbers from Redis.
        
        Args:
            game_id: Game ID
            
        Returns:
            Set of called numbers
        """
        try:
            redis = await self._get_redis()
            key = self._called_numbers_key(game_id)
            
            # Get all members from sorted set
            numbers = await redis.zrange(key, 0, -1)
            return {int(n) for n in numbers}
        
        except Exception as e:
            logger.warning("Failed to get called numbers from Redis", error=str(e), game_id=game_id)
            return set()

    async def publish_event(self, game_id: int, event_type: str, data: dict) -> bool:
        """
        Publish event to Redis Pub/Sub channel.
        
        Args:
            game_id: Game ID
            event_type: Event type
            data: Event data
            
        Returns:
            True if successful
        """
        try:
            redis = await self._get_redis()
            channel = self._events_channel(game_id)
            
            event = {
                "event": event_type,
                "game_id": game_id,
                "data": data,
            }
            
            await redis.publish(channel, json.dumps(event))
            logger.debug("Event published to Redis", game_id=game_id, event_type=event_type)
            return True
        
        except Exception as e:
            logger.warning("Failed to publish event to Redis", error=str(e), game_id=game_id)
            return False

    async def delete_game_state(self, game_id: int) -> bool:
        """
        Delete all game state from Redis.
        
        Args:
            game_id: Game ID
            
        Returns:
            True if successful
        """
        try:
            redis = await self._get_redis()
            
            keys_to_delete = [
                self._game_key(game_id),
                self._players_key(game_id),
                self._called_numbers_key(game_id),
            ]
            
            await redis.delete(*keys_to_delete)
            logger.debug("Game state deleted from Redis", game_id=game_id)
            return True
        
        except Exception as e:
            logger.warning("Failed to delete game state from Redis", error=str(e), game_id=game_id)
            return False
