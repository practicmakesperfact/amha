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
                # All 75 numbers called, no winner - house wins!
                await self._handle_no_winner_house_wins(game_id)
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
        Process winners: mark as winners, pay prizes, finish game.
        SINGLE WINNER MODE: First player(s) to win get prize pool divided equally.
        
        Handles simultaneous winners (multiple players win on same number call).
        
        Args:
            game_id: Game ID
            winners: List of (player, win_pattern) tuples - all detected on this number call
        """
        # Check if there's already a winner
        existing_winners = await self.player_repo.get_winners_by_game(game_id)
        if existing_winners:
            logger.warning("Game already has winner(s), ignoring new winners", game_id=game_id)
            return

        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        if not winners:
            return
        
        # Count simultaneous winners on this number call
        winner_count = len(winners)
        
        # Calculate prize per winner (split equally if simultaneous)
        prize_per_winner = round(game.prize_pool / winner_count, 2) if winner_count > 0 else 0
        
        logger.info(
            "Processing winners",
            game_id=game_id,
            winner_count=winner_count,
            total_prize=game.prize_pool,
            prize_per_winner=prize_per_winner,
        )
        
        # Mark all simultaneous winners and pay them
        for player, win_pattern in winners:
            # Mark player as winner (all get position 1 since they won simultaneously)
            player.is_winner = True
            player.status = PlayerStatus.WINNER
            player.win_pattern = win_pattern
            player.winning_position = 1

            await self.session.flush()

            # Log event
            from backend.models.bingo_models import GameEvent
            event = GameEvent(
                game_id=game_id,
                event_type=GameEventType.WINNER_DECLARED,
                user_id=player.user_id,
                player_id=player.id,
                description=f"Winner - {win_pattern} ({winner_count} simultaneous winner(s))",
                event_data=json.dumps({
                    "position": 1,
                    "win_pattern": win_pattern.value,
                    "simultaneous_winners": winner_count,
                    "prize_split": prize_per_winner,
                }),
            )
            self.session.add(event)

            await self.session.flush()

            # Pay winner their share of prize pool
            if prize_per_winner > 0:
                await self.prize_service.pay_winner(player, prize_per_winner, 1)
                await self.session.flush()
                
                logger.info(
                    "Prize paid to winner",
                    game_id=game_id,
                    user_id=player.user_id,
                    prize_amount=prize_per_winner,
                    total_winners=winner_count,
                )

        # IMMEDIATELY finish game after winner(s) found
        await self.game_service.finish_game(game_id)
        
        if winner_count == 1:
            logger.info(
                "Game finished - single winner takes all",
                game_id=game_id,
                user_id=winners[0][0].user_id,
                prize=prize_per_winner,
            )
        else:
            logger.info(
                "Game finished - simultaneous winners, prize split equally",
                game_id=game_id,
                winner_count=winner_count,
                prize_per_winner=prize_per_winner,
            )

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

    async def _handle_no_winner_house_wins(self, game_id: int) -> None:
        """
        Handle scenario when all 75 numbers called but no winner found.
        Prize pool goes to the house (admin user @HA with phone 0909425014).
        
        Args:
            game_id: Game ID
        """
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        logger.warning(
            "No winner after all numbers called - house wins!",
            game_id=game_id,
            prize_pool=game.prize_pool,
        )

        # Find admin user @HA (phone 0909425014)
        from backend.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.session)
        
        # Try to find admin by phone number
        from sqlalchemy import select
        from backend.models.models import User
        result = await self.session.execute(
            select(User).where(User.phone_number == "0909425014")
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            logger.error(
                "Admin user @HA (0909425014) not found! Cannot transfer house winnings.",
                game_id=game_id,
                prize_pool=game.prize_pool,
            )
            # Still finish the game even if admin not found
            await self.game_service.finish_game(game_id)
            return

        # Transfer prize pool to admin's main wallet
        if game.prize_pool > 0:
            # Lock admin user's wallet for update
            result = await self.session.execute(
                select(User).where(User.id == admin_user.id).with_for_update()
            )
            admin_user = result.scalar_one_or_none()

            if admin_user:
                balance_before = admin_user.main_wallet
                admin_user.main_wallet = round(admin_user.main_wallet + game.prize_pool, 2)
                balance_after = admin_user.main_wallet

                await self.session.flush()

                # Record wallet transaction
                from backend.repositories.wallet_transaction_repository import WalletTransactionRepository
                from backend.models.models import TransactionType
                wallet_tx_repo = WalletTransactionRepository(self.session)
                await wallet_tx_repo.create_transaction(
                    user_id=admin_user.id,
                    transaction_type=TransactionType.ADMIN_CREDIT,
                    amount=game.prize_pool,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    description=f"House wins - Game {game.game_number} (no winner)",
                )

                # Log event
                from backend.models.bingo_models import GameEvent
                event = GameEvent(
                    game_id=game_id,
                    event_type=GameEventType.GAME_FINISHED,
                    user_id=admin_user.id,
                    description=f"No winner found - House wins! Prize {game.prize_pool} Birr goes to @HA",
                    event_data=json.dumps({
                        "house_wins": True,
                        "prize_pool": float(game.prize_pool),
                        "admin_username": "HA",
                        "admin_phone": "0909425014",
                    }),
                )
                self.session.add(event)

                await self.session.flush()

                logger.info(
                    "House wins - prize transferred to admin @HA",
                    game_id=game_id,
                    prize_pool=game.prize_pool,
                    admin_user_id=admin_user.id,
                )

        # Finish the game
        await self.game_service.finish_game(game_id)
