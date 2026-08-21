"""
Game Engine Service — orchestrates game flow, winner detection, and prize distribution.
"""

import json
from typing import List, Optional, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import (
    BingoGame,
    GamePlayer,
    CalledNumber,
    PlayerStatus,
    WinPattern,
    GameEventType,
)
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.cartela_repository import CartelaRepository
from backend.repositories.called_number_repository import CalledNumberRepository
from backend.services.winner_validator_service import WinnerValidatorService
from backend.services.prize_distribution_service import PrizeDistributionService
from backend.services.number_caller_service import NumberCallerService
from backend.services.bingo_game_service import BingoGameService
from backend.core.logging import get_logger

logger = get_logger(__name__)


class GameEngineService:
    """Orchestrates game lifecycle, number calling, and winner detection."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.game_repo = BingoGameRepository(session)
        self.player_repo = GamePlayerRepository(session)
        self.cartela_repo = CartelaRepository(session)
        self.called_number_repo = CalledNumberRepository(session)
        self.winner_validator = WinnerValidatorService()
        self.prize_service = PrizeDistributionService(session)
        self.number_caller = NumberCallerService(session)
        self.game_service = BingoGameService(session)

    async def call_number_and_check_winners(
        self, game_id: int
    ) -> Tuple[Optional[CalledNumber], List[GamePlayer]]:
        """
        Call next number and check for winners.
        
        Args:
            game_id: Game ID
            
        Returns:
            (called_number, new_winners) tuple
        """
        async with self.session.begin_nested():
            # Call next number
            called_number = await self.number_caller.call_next_number(game_id)
            
            if not called_number:
                logger.warning("No more numbers to call", game_id=game_id)
                return None, []

            await self.session.flush()

            # Get all called numbers for this game
            called_numbers_set = await self.number_caller.get_called_numbers_set(game_id)

            # Check all active players for winners
            new_winners = await self._check_all_players_for_winners(
                game_id, called_numbers_set
            )

            # If winners found, pay prizes
            if new_winners:
                await self._process_winners(game_id, new_winners)

        logger.info(
            "Number called and winners checked",
            game_id=game_id,
            number=called_number.number if called_number else None,
            new_winners=len(new_winners),
        )

        return called_number, new_winners

    async def _check_all_players_for_winners(
        self, game_id: int, called_numbers: Set[int]
    ) -> List[Tuple[GamePlayer, WinPattern]]:
        """
        Check all active players for winning patterns.
        
        Returns:
            List of (player, win_pattern) tuples for new winners
        """
        players = await self.player_repo.get_players_by_game(game_id)
        new_winners = []

        for player in players:
            # Skip if already a winner
            if player.is_winner or player.status != PlayerStatus.ACTIVE:
                continue

            # Get player's cartela
            cartela = await self.cartela_repo.get_by_id(player.cartela_id)
            if not cartela:
                continue

            # Validate winner
            is_winner, win_pattern = self.winner_validator.validate_winner(
                cartela.numbers, called_numbers
            )

            if is_winner:
                new_winners.append((player, win_pattern))
                logger.info(
                    "Winner detected",
                    game_id=game_id,
                    user_id=player.user_id,
                    win_pattern=win_pattern,
                )

        return new_winners

    async def _process_winners(
        self, game_id: int, winners: List[Tuple[GamePlayer, WinPattern]]
    ) -> None:
        """
        Process winners: mark as winners, assign positions, pay prizes.
        
        Args:
            game_id: Game ID
            winners: List of (player, win_pattern) tuples
        """
        # Get current winner count to assign positions
        existing_winners = await self.player_repo.get_winners_by_game(game_id)
        next_position = len(existing_winners) + 1

        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        # Parse prize distribution
        try:
            prize_distribution = json.loads(game.prize_distribution) if game.prize_distribution else {}
        except json.JSONDecodeError:
            from backend.core.config import settings
            prize_distribution = {
                "first": settings.BINGO_FIRST_PRIZE_PERCENTAGE,
                "second": settings.BINGO_SECOND_PRIZE_PERCENTAGE,
                "third": settings.BINGO_THIRD_PRIZE_PERCENTAGE,
            }

        # Mark players as winners
        for idx, (player, win_pattern) in enumerate(winners):
            position = next_position + idx
            player.is_winner = True
            player.status = PlayerStatus.WINNER
            player.win_pattern = win_pattern
            player.winning_position = position

            await self.session.flush()

            # Log event
            from backend.models.bingo_models import GameEvent
            event = GameEvent(
                game_id=game_id,
                event_type=GameEventType.WINNER_DECLARED,
                user_id=player.user_id,
                player_id=player.id,
                description=f"Winner #{position} - {win_pattern}",
                event_data=json.dumps({
                    "position": position,
                    "win_pattern": win_pattern.value,
                }),
            )
            self.session.add(event)

        await self.session.flush()

        # Calculate and pay prizes
        all_winners = await self.player_repo.get_winners_by_game(game_id)
        
        # Only pay if 1-3 winners (configurable)
        if len(all_winners) <= 3:
            prize_amounts = self.prize_service.calculate_prize_amounts(
                prize_pool=game.prize_pool,
                winner_count=len(all_winners),
                prize_distribution=prize_distribution,
            )

            # Pay each winner who hasn't been paid yet
            for player in all_winners:
                if player.prize_amount == 0 and player.winning_position:
                    idx = player.winning_position - 1
                    if idx < len(prize_amounts):
                        prize = prize_amounts[idx]
                        if prize > 0:
                            await self.prize_service.pay_winner(
                                player, prize, player.winning_position
                            )
                            await self.session.flush()

        # Check if game should finish (3 winners or all numbers called)
        if len(all_winners) >= 3:
            await self.game_service.finish_game(game_id)
            logger.info("Game finished - 3 winners reached", game_id=game_id)

    async def get_player_stats(self, user_id: int) -> dict:
        """
        Calculate player statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Statistics dictionary
        """
        players = await self.player_repo.get_players_by_user(user_id, skip=0, limit=1000)

        games_played = len(players)
        games_won = sum(1 for p in players if p.is_winner)
        total_entry_fees = sum(p.entry_fee for p in players)
        total_winnings = sum(p.prize_amount for p in players)
        net_profit = total_winnings - total_entry_fees
        win_rate = (games_won / games_played * 100) if games_played > 0 else 0.0

        return {
            "user_id": user_id,
            "games_played": games_played,
            "games_won": games_won,
            "win_rate": round(win_rate, 2),
            "total_entry_fees": round(total_entry_fees, 2),
            "total_winnings": round(total_winnings, 2),
            "net_profit": round(net_profit, 2),
        }
