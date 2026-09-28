"""
Bingo game handler for Telegram bot.
Allows users to join games, view cartelas, and receive notifications.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from backend.bot.messages import NOT_REGISTERED_BALANCE
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.handlers.common import check_rate_limit, send_main_menu
from backend.keyboards.keyboards import main_menu_keyboard
from backend.services.user_service import UserService
from backend.services.bingo_game_service import BingoGameService
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.cartela_repository import CartelaRepository
from backend.repositories.called_number_repository import CalledNumberRepository
from backend.models.bingo_models import GameStatus

logger = get_logger(__name__)


async def bingo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle '🎲 Play Bingo' button - show available games."""
    if update.effective_user is None:
        return
    if await check_rate_limit(update):
        return

    tg_user = update.effective_user
    logger.info("Bingo menu requested", telegram_id=tg_user.id)

    try:
        factory = get_session_factory()
        async with factory() as session:
            service = UserService(session)
            user = await service.get_by_telegram_id(tg_user.id)

            if user is None or not user.is_registered:
                await update.effective_message.reply_text(
                    "❌ <b>Not Registered</b>\n\n"
                    "You need to register first to play Bingo.\n"
                    "Press <b>📝 Register</b> to get started.",
                    reply_markup=main_menu_keyboard(),
                    parse_mode="HTML",
                )
                return

            # Get available games
            game_repo = BingoGameRepository(session)
            waiting_games = await game_repo.get_waiting_games(skip=0, limit=10)
            playing_games = await game_repo.get_active_games(skip=0, limit=5)

            if not waiting_games and not playing_games:
                await update.effective_message.reply_text(
                    "🎲 <b>No Active Games</b>\n\n"
                    "There are no games available right now.\n"
                    "Check back later or contact support to create a game.",
                    reply_markup=main_menu_keyboard(),
                    parse_mode="HTML",
                )
                return

            # Build message
            msg = "🎲 <b>BINGO GAMES</b>\n\n"

            # Build inline keyboard
            keyboard = []

            if waiting_games:
                msg += "⏳ <b>Waiting to Start:</b>\n"
                for game in waiting_games:
                    player_repo = GamePlayerRepository(session)
                    player_count = await player_repo.get_active_players_count(game.id)
                    msg += f"  • Game #{game.game_number}\n"
                    msg += f"    Entry: {game.entry_fee} Birr\n"
                    msg += f"    Prize: {game.prize_pool} Birr\n"
                    msg += f"    Players: {player_count}/{game.max_players}\n\n"

                    keyboard.append([
                        InlineKeyboardButton(
                            f"🎮 Join Game #{game.game_number} ({game.entry_fee} Birr)",
                            callback_data=f"bingo:join:{game.id}"
                        )
                    ])

            if playing_games:
                msg += "\n🎮 <b>In Progress:</b>\n"
                for game in playing_games:
                    player_repo = GamePlayerRepository(session)
                    player_count = await player_repo.get_active_players_count(game.id)
                    msg += f"  • Game #{game.game_number}\n"
                    msg += f"    Prize: {game.prize_pool} Birr\n"
                    msg += f"    Players: {player_count}\n\n"

                    # Check if user is in this game
                    player = await player_repo.get_by_game_and_user(game.id, user.id)
                    if player:
                        keyboard.append([
                            InlineKeyboardButton(
                                f"📋 My Card - Game #{game.game_number}",
                                callback_data=f"bingo:card:{game.id}"
                            )
                        ])

            # Add "My Games" button
            keyboard.append([
                InlineKeyboardButton(
                    "📊 My Games History",
                    callback_data="bingo:my_games"
                )
            ])

            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else main_menu_keyboard()

            await update.effective_message.reply_text(
                msg,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )

    except Exception:
        logger.exception("Error in bingo_handler", telegram_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ Could not load games. Please try again.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )


async def bingo_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks for bingo actions."""
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    tg_user = update.effective_user
    if not tg_user:
        return

    data_parts = query.data.split(":")
    if len(data_parts) < 2 or data_parts[0] != "bingo":
        return

    action = data_parts[1]

    try:
        factory = get_session_factory()
        async with factory() as session:
            user_service = UserService(session)
            user = await user_service.get_by_telegram_id(tg_user.id)

            if not user or not user.is_registered:
                await query.edit_message_text(
                    "❌ You need to register first.",
                    parse_mode="HTML",
                )
                return

            if action == "join" and len(data_parts) >= 3:
                game_id = int(data_parts[2])
                await _handle_join_game(query, user, game_id, session)

            elif action == "card" and len(data_parts) >= 3:
                game_id = int(data_parts[2])
                await _handle_view_card(query, user, game_id, session)

            elif action == "my_games":
                await _handle_my_games(query, user, session)

    except Exception:
        logger.exception("Error in bingo_callback_handler", telegram_id=tg_user.id)
        await query.edit_message_text(
            "⚠️ An error occurred. Please try again.",
            parse_mode="HTML",
        )


async def _handle_join_game(query, user, game_id: int, session) -> None:
    """Handle joining a game."""
    try:
        async with session.begin():
            game_service = BingoGameService(session)
            player, cartela = await game_service.join_game(game_id, user.id)
            await session.commit()

        # Format cartela for display
        cartela_display = _format_cartela(cartela.numbers)

        await query.edit_message_text(
            f"✅ <b>Joined Game Successfully!</b>\n\n"
            f"🎫 <b>Your Bingo Card:</b>\n\n"
            f"{cartela_display}\n\n"
            f"Entry fee of <b>{player.entry_fee} Birr</b> has been deducted from your play wallet.\n\n"
            f"💡 <b>How to Win:</b>\n"
            f"• Complete any row, column, diagonal, or full card\n"
            f"• First to win gets the entire prize pool!\n"
            f"• If multiple players win on same number, prize is split equally\n\n"
            f"Good luck! 🍀",
            parse_mode="HTML",
        )

    except ValueError as e:
        await query.edit_message_text(
            f"❌ <b>Could Not Join Game</b>\n\n{str(e)}",
            parse_mode="HTML",
        )


async def _handle_view_card(query, user, game_id: int, session) -> None:
    """Handle viewing player's cartela."""
    cartela_repo = CartelaRepository(session)
    cartela = await cartela_repo.get_by_game_and_user(game_id, user.id)

    if not cartela:
        await query.edit_message_text(
            "❌ You are not in this game.",
            parse_mode="HTML",
        )
        return

    # Get called numbers
    called_number_repo = CalledNumberRepository(session)
    called_numbers_list = await called_number_repo.get_called_numbers_by_game(game_id)
    called_numbers = set(cn.number for cn in called_numbers_list)

    # Format cartela with marked numbers
    cartela_display = _format_cartela(cartela.numbers, called_numbers)

    # Get game info
    game_repo = BingoGameRepository(session)
    game = await game_repo.get_by_id(game_id)

    await query.edit_message_text(
        f"🎫 <b>Your Bingo Card</b>\n"
        f"Game #{game.game_number if game else game_id}\n\n"
        f"{cartela_display}\n\n"
        f"Numbers called: {len(called_numbers)}/75\n"
        f"✅ = Number has been called",
        parse_mode="HTML",
    )


async def _handle_my_games(query, user, session) -> None:
    """Handle viewing player's game history."""
    from backend.services.game_engine_service import GameEngineService

    engine = GameEngineService(session)
    stats = await engine.get_player_stats(user.id)

    player_repo = GamePlayerRepository(session)
    recent_players = await player_repo.get_players_by_user(user.id, skip=0, limit=5)

    msg = (
        f"📊 <b>Your Bingo Stats</b>\n\n"
        f"Games Played: {stats['games_played']}\n"
        f"Games Won: {stats['games_won']}\n"
        f"Win Rate: {stats['win_rate']}%\n"
        f"Total Entry Fees: {stats['total_entry_fees']} Birr\n"
        f"Total Winnings: {stats['total_winnings']} Birr\n"
        f"Net Profit: {stats['net_profit']} Birr\n\n"
    )

    if recent_players:
        msg += "<b>Recent Games:</b>\n"
        game_repo = BingoGameRepository(session)
        for player in recent_players[:5]:
            game = await game_repo.get_by_id(player.game_id)
            if game:
                status_emoji = "✅" if player.is_winner else "❌"
                msg += f"{status_emoji} Game #{game.game_number} - "
                if player.is_winner:
                    msg += f"Won {player.prize_amount} Birr\n"
                else:
                    msg += f"Lost {player.entry_fee} Birr\n"

    await query.edit_message_text(msg, parse_mode="HTML")


def _format_cartela(numbers: list[list[int]], called: set[int] = None) -> str:
    """Format cartela numbers as a text grid with B-I-N-G-O header."""
    if called is None:
        called = set()

    lines = []
    lines.append("  B    I    N    G    O")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")

    for row in numbers:
        row_str = ""
        for num in row:
            if num == 0:  # FREE space
                row_str += " FREE"
            elif num in called:
                row_str += f" ✅{num:2d}"
            else:
                row_str += f"  {num:2d} "
        lines.append(row_str)

    return "\n".join(lines)
