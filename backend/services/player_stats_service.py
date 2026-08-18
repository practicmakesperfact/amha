"""
Player Statistics Service — calculate player game statistics.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.models.bingo_models import GamePlayer, PlayerStatus
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.core.logging import get_logger

logger = get_logger(__name__)


class PlayerStatsService:
    """Service for calculating player statistics."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.player_repo = GamePlayerRepository(session)

    async def get_player_stats(self, user_id: int) -> dict:
        """
        Calculate comprehensive statistics for a player.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with statistics
        """
        # Get all player records for this user
        all_players = await self.player_repo.get_players_by_user(user_id, skip=0, limit=1000)
        
        # Calculate statistics
        games_played = len(all_players)
        
        # Count games won
        games_won = sum(1 for p in all_players if p.is_winner)
        
        # Calculate win rate
        win_rate = (games_won / games_played * 100) if games_played > 0 else 0.0
        
        # Calculate financial stats
        total_entry_fees = sum(p.entry_fee for p in all_players)
        total_winnings = sum(p.prize_amount for p in all_players)
        net_profit = total_winnings - total_entry_fees
        
        # Get win breakdown by position
        first_place_wins = sum(1 for p in all_players if p.winning_position == 1)
        second_place_wins = sum(1 for p in all_players if p.winning_position == 2)
        third_place_wins = sum(1 for p in all_players if p.winning_position == 3)
        
        # Get most recent games
        recent_games = sorted(all_players, key=lambda p: p.joined_at, reverse=True)[:10]
        
        stats = {
            "user_id": user_id,
            "games_played": games_played,
            "games_won": games_won,
            "win_rate": round(win_rate, 2),
            "total_entry_fees": round(total_entry_fees, 2),
            "total_winnings": round(total_winnings, 2),
            "net_profit": round(net_profit, 2),
            "first_place_wins": first_place_wins,
            "second_place_wins": second_place_wins,
            "third_place_wins": third_place_wins,
            "recent_game_count": len(recent_games),
        }
        
        logger.debug("Player stats calculated", user_id=user_id, games_played=games_played)
        return stats
