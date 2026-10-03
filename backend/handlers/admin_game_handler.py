"""
Admin game management handler for Telegram bot.
Allows admins to create, start, pause, resume, and cancel games via bot commands.
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.services.user_service import UserService
from backend.services.bingo_game_service import BingoGameService
from backend.services.game_engine_service import GameEngineService
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.keyboards.keyboards import main_menu_keyboard
from backend.models.bingo_models import GameStatus

logger = get_logger(__name__)


async def admin_create_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /admin_create_game command.
    Usage: /admin_create_game <entry_fee> <max_players> <min_players>
    Example: /admin_create_game 10 50 2
    """
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    
    # Check if user is admin
    factory = get_session_factory()
    async with factory() as session:
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(tg_user.id)
        
        if not user or not user.is_admin:
            await update.effective_message.reply_text(
                "❌ <b>Access Denied</b>\n\n"
                "This command is only for administrators.",
                parse_mode="HTML",
                reply_markup=main_menu_keyboard(),
            )
            return

    # Parse arguments
    if not context.args or len(context.args) != 3:
        await update.effective_message.reply_text(
            "❌ <b>Invalid Command</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/admin_create_game &lt;entry_fee&gt; &lt;max_players&gt; &lt;min_players&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/admin_create_game 10 50 2</code>\n\n"
            "This creates a game with:\n"
            "• Entry fee: 10 Birr\n"
            "• Maximum players: 50\n"
            "• Minimum players: 2",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
        return

    try:
        entry_fee = float(context.args[0])
        max_players = int(context.args[1])
        min_players = int(context.args[2])

        # Validate inputs
        if entry_fee < 10:
            await update.effective_message.reply_text(
                "❌ Entry fee must be at least 10 Birr.",
                parse_mode="HTML",
            )
            return

        if max_players < 2 or max_players > 1000:
            await update.effective_message.reply_text(
                "❌ Max players must be between 2 and 1000.",
                parse_mode="HTML",
            )
            return

        if min_players < 1 or min_players > max_players:
            await update.effective_message.reply_text(
                f"❌ Min players must be between 1 and {max_players}.",
                parse_mode="HTML",
            )
            return

        # Create game
        async with factory() as session:
            game_service = BingoGameService(session)
            game = await game_service.create_game(
                entry_fee=entry_fee,
                max_players=max_players,
                min_players=min_players,
            )
            await session.commit()

        logger.info(
            "Admin created game",
            admin_id=tg_user.id,
            game_id=game.id,
            game_number=game.game_number,
        )

        await update.effective_message.reply_text(
            f"✅ <b>Game Created Successfully!</b>\n\n"
            f"🎮 <b>Game #{game.game_number}</b>\n"
            f"Entry Fee: {game.entry_fee} Birr\n"
            f"Max Players: {game.max_players}\n"
            f"Min Players: {game.min_players}\n"
            f"Status: {game.status.value}\n"
            f"Prize Pool: {game.prize_pool} Birr\n\n"
            f"Game ID: <code>{game.id}</code>\n\n"
            f"Players can now join this game via the bot.\n"
            f"Game will auto-start when {min_players}+ players join.\n\n"
            f"<b>Commands:</b>\n"
            f"<code>/admin_start_game {game.id}</code> - Force start\n"
            f"<code>/admin_cancel_game {game.id}</code> - Cancel game",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )

    except ValueError:
        await update.effective_message.reply_text(
            "❌ <b>Invalid Values</b>\n\n"
            "Entry fee must be a number (e.g., 10.5)\n"
            "Players must be whole numbers.",
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Error creating game", admin_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ Could not create game. Please try again.",
            parse_mode="HTML",
        )


async def admin_start_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /admin_start_game command.
    Usage: /admin_start_game <game_id>
    Example: /admin_start_game 1
    """
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    
    # Check if user is admin
    factory = get_session_factory()
    async with factory() as session:
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(tg_user.id)
        
        if not user or not user.is_admin:
            await update.effective_message.reply_text(
                "❌ Access denied. Admin only.",
                parse_mode="HTML",
            )
            return

    # Parse arguments
    if not context.args or len(context.args) != 1:
        await update.effective_message.reply_text(
            "❌ <b>Invalid Command</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/admin_start_game &lt;game_id&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/admin_start_game 1</code>",
            parse_mode="HTML",
        )
        return

    try:
        game_id = int(context.args[0])

        async with factory() as session:
            engine = GameEngineService(session)
            await engine.start_game(game_id)
            await session.commit()

        logger.info(
            "Admin started game",
            admin_id=tg_user.id,
            game_id=game_id,
        )

        await update.effective_message.reply_text(
            f"✅ <b>Game Started!</b>\n\n"
            f"Game ID: {game_id}\n"
            f"Status: PLAYING\n\n"
            f"Numbers will be called automatically every 5 seconds.\n"
            f"Players will receive updates via WebSocket and bot notifications.",
            parse_mode="HTML",
        )

    except ValueError as e:
        await update.effective_message.reply_text(
            f"❌ <b>Could Not Start Game</b>\n\n{str(e)}",
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Error starting game", admin_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ Could not start game. Check game ID and try again.",
            parse_mode="HTML",
        )


async def admin_cancel_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /admin_cancel_game command.
    Usage: /admin_cancel_game <game_id>
    Example: /admin_cancel_game 1
    """
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    
    # Check if user is admin
    factory = get_session_factory()
    async with factory() as session:
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(tg_user.id)
        
        if not user or not user.is_admin:
            await update.effective_message.reply_text(
                "❌ Access denied. Admin only.",
                parse_mode="HTML",
            )
            return

    # Parse arguments
    if not context.args or len(context.args) != 1:
        await update.effective_message.reply_text(
            "❌ <b>Invalid Command</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/admin_cancel_game &lt;game_id&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/admin_cancel_game 1</code>",
            parse_mode="HTML",
        )
        return

    try:
        game_id = int(context.args[0])

        async with factory() as session:
            engine = GameEngineService(session)
            await engine.cancel_game(game_id)
            await session.commit()

        logger.info(
            "Admin cancelled game",
            admin_id=tg_user.id,
            game_id=game_id,
        )

        await update.effective_message.reply_text(
            f"✅ <b>Game Cancelled</b>\n\n"
            f"Game ID: {game_id}\n\n"
            f"All players have been refunded their entry fees.",
            parse_mode="HTML",
        )

    except ValueError as e:
        await update.effective_message.reply_text(
            f"❌ <b>Could Not Cancel Game</b>\n\n{str(e)}",
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Error cancelling game", admin_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ Could not cancel game. Check game ID and try again.",
            parse_mode="HTML",
        )


async def admin_list_games_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /admin_list_games command.
    Shows all active and recent games.
    """
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    
    # Check if user is admin
    factory = get_session_factory()
    async with factory() as session:
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(tg_user.id)
        
        if not user or not user.is_admin:
            await update.effective_message.reply_text(
                "❌ Access denied. Admin only.",
                parse_mode="HTML",
            )
            return

        # Get games
        game_repo = BingoGameRepository(session)
        waiting_games = await game_repo.get_waiting_games(skip=0, limit=10)
        active_games = await game_repo.get_active_games(skip=0, limit=10)
        finished_games = await game_repo.get_finished_games(skip=0, limit=5)

        msg = "🎮 <b>GAME MANAGEMENT</b>\n\n"

        if waiting_games:
            msg += "⏳ <b>Waiting to Start:</b>\n"
            for game in waiting_games:
                player_repo = GamePlayerRepository(session)
                player_count = await player_repo.get_active_players_count(game.id)
                msg += (
                    f"  • Game #{game.game_number} (ID: {game.id})\n"
                    f"    Entry: {game.entry_fee} Birr\n"
                    f"    Prize: {game.prize_pool} Birr\n"
                    f"    Players: {player_count}/{game.max_players} "
                    f"(min: {game.min_players})\n"
                )
                if player_count >= game.min_players:
                    msg += f"    ✅ Ready to start!\n"
                msg += "\n"

        if active_games:
            msg += "🎲 <b>In Progress:</b>\n"
            for game in active_games:
                player_repo = GamePlayerRepository(session)
                player_count = await player_repo.get_active_players_count(game.id)
                msg += (
                    f"  • Game #{game.game_number} (ID: {game.id})\n"
                    f"    Status: {game.status.value}\n"
                    f"    Prize: {game.prize_pool} Birr\n"
                    f"    Players: {player_count}\n\n"
                )

        if finished_games:
            msg += "🏁 <b>Recently Finished:</b>\n"
            for game in finished_games[:3]:
                msg += (
                    f"  • Game #{game.game_number} - "
                    f"{game.prize_pool} Birr\n"
                )

        if not waiting_games and not active_games and not finished_games:
            msg += "No games found.\n\n"

        msg += "\n<b>Commands:</b>\n"
        msg += "<code>/admin_create_game 10 50 2</code>\n"
        msg += "<code>/admin_start_game &lt;id&gt;</code>\n"
        msg += "<code>/admin_cancel_game &lt;id&gt;</code>"

        await update.effective_message.reply_text(
            msg,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )

    except Exception:
        logger.exception("Error listing games", admin_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ Could not load games.",
            parse_mode="HTML",
        )


async def admin_game_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /admin_stats command.
    Shows platform statistics.
    """
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    
    # Check if user is admin
    factory = get_session_factory()
    async with factory() as session:
        user_service = UserService(session)
        user = await user_service.get_by_telegram_id(tg_user.id)
        
        if not user or not user.is_admin:
            await update.effective_message.reply_text(
                "❌ Access denied. Admin only.",
                parse_mode="HTML",
            )
            return

        try:
            game_repo = BingoGameRepository(session)
            
            # Get counts
            from sqlalchemy import select, func
            from backend.models.bingo_models import BingoGame, GamePlayer
            
            total_games = await session.scalar(
                select(func.count(BingoGame.id))
            )
            
            waiting_count = await session.scalar(
                select(func.count(BingoGame.id))
                .where(BingoGame.status == GameStatus.WAITING)
            )
            
            active_count = await session.scalar(
                select(func.count(BingoGame.id))
                .where(BingoGame.status == GameStatus.PLAYING)
            )
            
            finished_count = await session.scalar(
                select(func.count(BingoGame.id))
                .where(BingoGame.status == GameStatus.FINISHED)
            )
            
            total_players = await session.scalar(
                select(func.count(GamePlayer.id))
            )
            
            total_prize_pool = await session.scalar(
                select(func.sum(BingoGame.prize_pool))
                .where(BingoGame.status == GameStatus.FINISHED)
            ) or 0

            msg = (
                f"📊 <b>PLATFORM STATISTICS</b>\n\n"
                f"<b>Games:</b>\n"
                f"  Total Games: {total_games or 0}\n"
                f"  ⏳ Waiting: {waiting_count or 0}\n"
                f"  🎲 Active: {active_count or 0}\n"
                f"  🏁 Finished: {finished_count or 0}\n\n"
                f"<b>Players:</b>\n"
                f"  Total Participations: {total_players or 0}\n\n"
                f"<b>Financial:</b>\n"
                f"  Total Prizes Distributed: {total_prize_pool:.2f} Birr\n\n"
                f"Use <code>/admin_list_games</code> to see game details."
            )

            await update.effective_message.reply_text(
                msg,
                parse_mode="HTML",
                reply_markup=main_menu_keyboard(),
            )

        except Exception:
            logger.exception("Error getting stats", admin_id=tg_user.id)
            await update.effective_message.reply_text(
                "⚠️ Could not load statistics.",
                parse_mode="HTML",
            )
