"""
Prize Distribution Service — handles prize calculation and payment for winners.
"""

import json
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import GamePlayer, BingoGame, GameEventType
from backend.models.models import User, TransactionType, AuditAction
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class PrizeDistributionService:
    """Service for calculating and distributing prizes to winners."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.game_repo = BingoGameRepository(session)
        self.player_repo = GamePlayerRepository(session)

    def calculate_prize_amounts(
        self,
        prize_pool: float,
        winner_count: int,
        prize_distribution: Dict[str, int],
    ) -> List[float]:
        """
        Calculate prize amounts for each winner position.
        
        Args:
            prize_pool: Total prize pool
            winner_count: Number of winners
            prize_distribution: Distribution config (e.g., {"first": 60, "second": 30, "third": 10})
            
        Returns:
            List of prize amounts [first_prize, second_prize, ...]
        """
        if winner_count == 0:
            return []
        
        prizes = []
        
        if winner_count == 1:
            # Single winner gets entire pool
            prizes.append(round(prize_pool, 2))
        elif winner_count == 2:
            # Two winners split based on first/second percentages
            first_pct = prize_distribution.get("first", 60)
            second_pct = prize_distribution.get("second", 40)
            total_pct = first_pct + second_pct
            
            prizes.append(round(prize_pool * first_pct / total_pct, 2))
            prizes.append(round(prize_pool * second_pct / total_pct, 2))
        elif winner_count >= 3:
            # Three or more winners
            first_pct = prize_distribution.get("first", 60)
            second_pct = prize_distribution.get("second", 30)
            third_pct = prize_distribution.get("third", 10)
            total_pct = first_pct + second_pct + third_pct
            
            prizes.append(round(prize_pool * first_pct / total_pct, 2))
            prizes.append(round(prize_pool * second_pct / total_pct, 2))
            prizes.append(round(prize_pool * third_pct / total_pct, 2))
            
            # Additional winners split third place
            if winner_count > 3:
                third_prize = prizes[2]
                additional_count = winner_count - 2
                prizes[2] = round(third_prize / additional_count, 2)
                for _ in range(3, winner_count):
                    prizes.append(prizes[2])
        
        return prizes

    async def pay_winner(
        self,
        player: GamePlayer,
        prize_amount: float,
        winning_position: int,
    ) -> User:
        """
        Pay prize to a winner.
        
        Args:
            player: GamePlayer instance
            prize_amount: Amount to pay
            winning_position: Winner position (1, 2, 3, ...)
            
        Returns:
            Updated User instance
            
        Raises:
            ValueError: If player already paid or user not found
        """
        if player.prize_amount > 0:
            raise ValueError("Winner already paid")

        async with self.session.begin_nested():
            # Lock user for update
            from sqlalchemy import select
            result = await self.session.execute(
                select(User).where(User.id == player.user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")

            # Credit wallet
            balance_before = user.main_wallet
            user.main_wallet = round(user.main_wallet + prize_amount, 2)
            balance_after = user.main_wallet
            
            # Update player
            player.prize_amount = prize_amount
            player.winning_position = winning_position
            
            # Record wallet transaction
            try:
                from backend.repositories.wallet_transaction_repository import WalletTransactionRepository
                wallet_tx_repo = WalletTransactionRepository(self.session)
                await wallet_tx_repo.create_transaction(
                    user_id=user.id,
                    transaction_type=TransactionType.ADMIN_CREDIT,
                    amount=prize_amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    description=f"Bingo prize - Position {winning_position}",
                )
            except Exception as e:
                logger.warning("Could not record wallet transaction", error=str(e))

            # Record audit log
            try:
                from backend.repositories.audit_log_repository import AuditLogRepository
                audit_repo = AuditLogRepository(self.session)
                await audit_repo.create_log(
                    action=AuditAction.WALLET_CREDITED,
                    user_id=user.id,
                    amount=prize_amount,
                    description=f"Bingo prize - Game {player.game_id}, Position {winning_position}",
                    extra_data=json.dumps({
                        "game_id": player.game_id,
                        "player_id": player.id,
                        "winning_position": winning_position,
                    }),
                )
            except Exception as e:
                logger.warning("Could not record audit log", error=str(e))

            # Log game event
            from backend.models.bingo_models import GameEvent
            event = GameEvent(
                game_id=player.game_id,
                event_type=GameEventType.PRIZE_PAID,
                user_id=user.id,
                player_id=player.id,
                description=f"Prize {prize_amount} ETB paid to winner position {winning_position}",
                event_data=json.dumps({"prize_amount": prize_amount, "position": winning_position}),
            )
            self.session.add(event)

            await self.session.flush()
            await self.session.refresh(user)

        logger.info(
            "Prize paid to winner",
            game_id=player.game_id,
            user_id=user.id,
            prize_amount=prize_amount,
            winning_position=winning_position,
        )

        return user

    async def distribute_prizes(self, game_id: int) -> List[GamePlayer]:
        """
        Distribute prizes to all winners in a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            List of updated GamePlayer instances
        """
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            raise ValueError("Game not found")

        # Get all winners ordered by position
        winners = await self.player_repo.get_winners_by_game(game_id)
        
        if not winners:
            logger.warning("No winners found for prize distribution", game_id=game_id)
            return []

        # Parse prize distribution config
        try:
            prize_distribution = json.loads(game.prize_distribution) if game.prize_distribution else {}
        except json.JSONDecodeError:
            prize_distribution = {}

        if not prize_distribution:
            prize_distribution = {
                "first": settings.BINGO_FIRST_PRIZE_PERCENTAGE,
                "second": settings.BINGO_SECOND_PRIZE_PERCENTAGE,
                "third": settings.BINGO_THIRD_PRIZE_PERCENTAGE,
            }

        # Calculate prize amounts
        prize_amounts = self.calculate_prize_amounts(
            prize_pool=game.prize_pool,
            winner_count=len(winners),
            prize_distribution=prize_distribution,
        )

        # Pay each winner
        updated_players = []
        for idx, player in enumerate(winners):
            if idx < len(prize_amounts):
                prize = prize_amounts[idx]
                if prize > 0 and player.prize_amount == 0:  # Only pay if not already paid
                    await self.pay_winner(player, prize, idx + 1)
                    updated_players.append(player)

        logger.info(
            "Prizes distributed",
            game_id=game_id,
            winner_count=len(winners),
            total_distributed=sum(prize_amounts),
        )

        return updated_players
