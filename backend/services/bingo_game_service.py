"""
Bingo Game Service — business logic for game lifecycle management.
"""

import json
from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import (
    BingoGame,
    GamePlayer,
    Cartela,
    GameStatus,
    PlayerStatus,
    GameEventType,
    WinPattern,
)
from backend.models.models import User, TransactionType, AuditAction
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.cartela_repository import CartelaRepository
from backend.repositories.game_event_repository import GameEventRepository
from backend.repositories.user_repository import UserRepository
from backend.services.cartela_generator_service import CartelaGeneratorService
from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class BingoGameService:
    """Service for managing Bingo game lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.game_repo = BingoGameRepository(session)
        self.player_repo = GamePlayerRepository(session)
        self.cartela_repo = CartelaRepository(session)
        self.event_repo = GameEventRepository(session)
        self.user_repo = UserRepository(session)
        self.cartela_generator = CartelaGeneratorService()

    async def create_game(
        self,
        entry_fee: float,
        max_players: Optional[int] = None,
        min_players: Optional[int] = None,
        created_by: Optional[int] = None,
        prize_distribution: Optional[dict] = None,
    ) -> BingoGame:
        """
        Create a new Bingo game.
        
        Args:
            entry_fee: Entry fee per player
            max_players: Maximum players (default from config)
            min_players: Minimum players (default from config)
            created_by: Admin user ID who created the game
            prize_distribution: Prize distribution percentages
            
        Returns:
            Created BingoGame instance
        """
        # Validate entry fee
        if entry_fee < settings.BINGO_MIN_ENTRY_FEE:
            raise ValueError(f"Entry fee must be at least {settings.BINGO_MIN_ENTRY_FEE} ETB")
        if entry_fee > settings.BINGO_MAX_ENTRY_FEE:
            raise ValueError(f"Entry fee cannot exceed {settings.BINGO_MAX_ENTRY_FEE} ETB")

        # Set defaults
        if max_players is None:
            max_players = settings.BINGO_MAX_PLAYERS
        if min_players is None:
            min_players = settings.BINGO_MIN_PLAYERS

        if max_players < min_players:
            raise ValueError("Max players must be greater than or equal to min players")

        # Generate unique game number
        import secrets
        game_number = f"BG{datetime.utcnow().strftime('%Y%m%d')}{secrets.token_hex(4).upper()}"

        # Set default prize distribution
        if prize_distribution is None:
            prize_distribution = {
                "first": settings.BINGO_FIRST_PRIZE_PERCENTAGE,
                "second": settings.BINGO_SECOND_PRIZE_PERCENTAGE,
                "third": settings.BINGO_THIRD_PRIZE_PERCENTAGE,
            }

        async with self.session.begin_nested():
            game = BingoGame(
                game_number=game_number,
                entry_fee=entry_fee,
                prize_pool=0.0,
                max_players=max_players,
                min_players=min_players,
                status=GameStatus.WAITING,
                created_by=created_by,
                prize_distribution=json.dumps(prize_distribution),
                numbers_called_count=0,
            )
            self.session.add(game)
            await self.session.flush()
            await self.session.refresh(game)

            # Log game creation event
            await self._log_event(
                game_id=game.id,
                event_type=GameEventType.GAME_CREATED,
                description=f"Game {game_number} created with entry fee {entry_fee} ETB",
            )

        logger.info("Game created", game_id=game.id, game_number=game_number, entry_fee=entry_fee)
        return game

    async def join_game(self, game_id: int, user_id: int) -> Tuple[GamePlayer, Cartela]:
        """
        Player joins a game - atomically deducts entry fee and assigns cartela.
        
        Args:
            game_id: Game ID to join
            user_id: User ID joining
            
        Returns:
            (GamePlayer, Cartela) tuple
            
        Raises:
            ValueError: If game is not joinable, user already joined, or insufficient balance
        """
        async with self.session.begin_nested():
            # Lock game and user for update
            game = await self.game_repo.get_by_id(game_id)
            if not game:
                raise ValueError("Game not found")

            # Verify game is joinable
            if game.status != GameStatus.WAITING:
                raise ValueError(f"Cannot join game in status {game.status}")

            # Check player count
            player_count = await self.player_repo.get_active_players_count(game_id)
            if player_count >= game.max_players:
                raise ValueError("Game is full")

            # Check if user already joined
            existing_player = await self.player_repo.get_by_game_and_user(game_id, user_id)
            if existing_player:
                raise ValueError("User already joined this game")

            # Lock user and deduct entry fee
            from sqlalchemy import select
            result = await self.session.execute(
                select(User).where(User.id == user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError("User not found")

            if not user.is_registered:
                raise ValueError("User must be registered to join games")

            if user.main_wallet < game.entry_fee:
                raise ValueError(
                    f"Insufficient balance. Need {game.entry_fee} ETB, have {user.main_wallet} ETB"
                )

            # Deduct entry fee
            balance_before = user.main_wallet
            user.main_wallet = round(user.main_wallet - game.entry_fee, 2)
            balance_after = user.main_wallet

            # Record wallet transaction
            try:
                from backend.repositories.wallet_transaction_repository import WalletTransactionRepository
                wallet_tx_repo = WalletTransactionRepository(self.session)
                await wallet_tx_repo.create_transaction(
                    user_id=user_id,
                    transaction_type=TransactionType.ADMIN_DEBIT,
                    amount=game.entry_fee,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    description=f"Bingo entry fee - Game {game.game_number}",
                )
            except Exception as e:
                logger.warning("Could not record wallet transaction", error=str(e))

            # Update prize pool
            game.prize_pool = round(game.prize_pool + game.entry_fee, 2)

            # Generate cartela
            cartela_data = self.cartela_generator.generate_cartela()
            cartela_json = json.dumps(cartela_data)
            cartela_number = self.cartela_generator.generate_cartela_number(game_id, user_id)

            cartela = Cartela(
                game_id=game_id,
                user_id=user_id,
                numbers=cartela_json,
                cartela_number=cartela_number,
            )
            self.session.add(cartela)
            await self.session.flush()
            await self.session.refresh(cartela)

            # Create game player
            player = GamePlayer(
                game_id=game_id,
                user_id=user_id,
                cartela_id=cartela.id,
                entry_fee=game.entry_fee,
                status=PlayerStatus.JOINED,
                prize_amount=0.0,
                is_winner=False,
            )
            self.session.add(player)
            await self.session.flush()
            await self.session.refresh(player)

            # Log event
            await self._log_event(
                game_id=game_id,
                event_type=GameEventType.PLAYER_JOINED,
                user_id=user_id,
                player_id=player.id,
                description=f"User {user_id} joined game {game.game_number}",
            )

            # Record audit log
            try:
                from backend.repositories.audit_log_repository import AuditLogRepository
                audit_repo = AuditLogRepository(self.session)
                await audit_repo.create_log(
                    action=AuditAction.WALLET_DEBITED,
                    user_id=user_id,
                    amount=game.entry_fee,
                    description=f"Bingo game entry - {game.game_number}",
                    extra_data=json.dumps({"game_id": game_id, "player_id": player.id}),
                )
            except Exception as e:
                logger.warning("Could not record audit log", error=str(e))

        logger.info(
            "Player joined game",
            game_id=game_id,
            user_id=user_id,
            entry_fee=game.entry_fee,
            cartela_number=cartela_number,
        )

        return player, cartela

    async def _log_event(
        self,
        game_id: int,
        event_type: GameEventType,
        user_id: Optional[int] = None,
        player_id: Optional[int] = None,
        description: Optional[str] = None,
        event_data: Optional[dict] = None,
    ):
        """Log a game event."""
        from backend.models.bingo_models import GameEvent
        
        event = GameEvent(
            game_id=game_id,
            event_type=event_type,
            user_id=user_id,
            player_id=player_id,
            description=description,
            event_data=json.dumps(event_data) if event_data else None,
        )
        self.session.add(event)
        await self.session.flush()


    async def start_game(self, game_id: int) -> BingoGame:
        """Start a game if minimum players met."""
        async with self.session.begin_nested():
            game = await self.game_repo.get_by_id(game_id)
            if not game:
                raise ValueError("Game not found")

            if game.status != GameStatus.WAITING:
                raise ValueError(f"Cannot start game in status {game.status}")

            player_count = await self.player_repo.get_active_players_count(game_id)
            if player_count < game.min_players:
                raise ValueError(f"Need at least {game.min_players} players (have {player_count})")

            game = await self.game_repo.update_status(game_id, GameStatus.PLAYING)
            game.started_at = datetime.utcnow()

            players = await self.player_repo.get_players_by_game(game_id)
            for player in players:
                if player.status == PlayerStatus.JOINED:
                    player.status = PlayerStatus.ACTIVE

            await self.session.flush()

            await self._log_event(
                game_id=game_id,
                event_type=GameEventType.GAME_STARTED,
                description=f"Game {game.game_number} started with {player_count} players",
                event_data={"player_count": player_count},
            )

        logger.info("Game started", game_id=game_id, player_count=player_count)
        return game

    async def pause_game(self, game_id: int) -> BingoGame:
        """Pause a running game."""
        async with self.session.begin_nested():
            game = await self.game_repo.get_by_id(game_id)
            if not game:
                raise ValueError("Game not found")

            if game.status != GameStatus.PLAYING:
                raise ValueError(f"Cannot pause game in status {game.status}")

            game = await self.game_repo.update_status(game_id, GameStatus.PAUSED)
            game.paused_at = datetime.utcnow()

            await self.session.flush()
            await self._log_event(game_id=game_id, event_type=GameEventType.GAME_PAUSED, description=f"Game {game.game_number} paused")

        logger.info("Game paused", game_id=game_id)
        return game

    async def resume_game(self, game_id: int) -> BingoGame:
        """Resume a paused game."""
        async with self.session.begin_nested():
            game = await self.game_repo.get_by_id(game_id)
            if not game:
                raise ValueError("Game not found")

            if game.status != GameStatus.PAUSED:
                raise ValueError(f"Cannot resume game in status {game.status}")

            game = await self.game_repo.update_status(game_id, GameStatus.PLAYING)
            game.paused_at = None

            await self.session.flush()
            await self._log_event(game_id=game_id, event_type=GameEventType.GAME_RESUMED, description=f"Game {game.game_number} resumed")

        logger.info("Game resumed", game_id=game_id)
        return game

    async def finish_game(self, game_id: int) -> BingoGame:
        """Finish a game."""
        async with self.session.begin_nested():
            game = await self.game_repo.get_by_id(game_id)
            if not game:
                raise ValueError("Game not found")

            if game.status == GameStatus.FINISHED:
                raise ValueError("Game already finished")

            game = await self.game_repo.update_status(game_id, GameStatus.FINISHED)
            game.finished_at = datetime.utcnow()

            await self.session.flush()
            await self._log_event(game_id=game_id, event_type=GameEventType.GAME_FINISHED, description=f"Game {game.game_number} finished")

        logger.info("Game finished", game_id=game_id)
        return game

    async def refund_all_players(self, game_id: int) -> int:
        """Refund all players in a cancelled game. Idempotent."""
        refund_count = 0
        
        async with self.session.begin_nested():
            players = await self.player_repo.get_players_by_game(game_id)
            
            for player in players:
                if player.entry_fee > 0 and player.prize_amount == 0:
                    from sqlalchemy import select
                    result = await self.session.execute(
                        select(User).where(User.id == player.user_id).with_for_update()
                    )
                    user = result.scalar_one_or_none()
                    
                    if user:
                        balance_before = user.main_wallet
                        user.main_wallet = round(user.main_wallet + player.entry_fee, 2)
                        balance_after = user.main_wallet
                        
                        player.prize_amount = player.entry_fee
                        
                        try:
                            from backend.repositories.wallet_transaction_repository import WalletTransactionRepository
                            wallet_tx_repo = WalletTransactionRepository(self.session)
                            await wallet_tx_repo.create_transaction(
                                user_id=user.id,
                                transaction_type=TransactionType.ADMIN_CREDIT,
                                amount=player.entry_fee,
                                balance_before=balance_before,
                                balance_after=balance_after,
                                description=f"Refund - Game cancelled",
                            )
                        except Exception as e:
                            logger.warning("Could not record wallet transaction", error=str(e))
                        
                        refund_count += 1

            await self.session.flush()

        logger.info("Players refunded", game_id=game_id, refund_count=refund_count)
        return refund_count
