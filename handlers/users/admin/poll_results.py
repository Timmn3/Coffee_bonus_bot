from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import ADMIN_IE, CODER
from loader import dp
from utils.db_api.shemas.polls import Polls
from utils.db_api.poll_commands import build_stats_text, get_poll

POLL_STAT_REFRESH = "poll_stat_refresh"

def _is_admin(user_id: int) -> bool:
    return user_id in {int(ADMIN_IE), int(CODER)}

def _build_stat_kb(poll_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="🔄 Обновить", callback_data=f"{POLL_STAT_REFRESH}:{poll_id}"))
    return kb

@dp.message_handler(commands=["poll_results"])
async def cmd_poll_results(message: types.Message) -> None:
    """Показать статистику последнего опроса текущего админа (WHERE admin_chat_id = you)."""
    user_id = int(message.from_user.id)
    if not _is_admin(user_id):
        await message.answer("⛔ Нет доступа.")
        return

    poll = await Polls.query.where(Polls.admin_chat_id == user_id).order_by(Polls.id.desc()).gino.first()
    if not poll:
        await message.answer("Опросов для вашего аккаунта пока нет.")
        return

    stats_text, total = build_stats_text(poll.question, poll.options or [], poll.votes or [])
    suffix = f"\n\n<b>Всего голосов:</b> {total}"
    await message.answer(stats_text + suffix, reply_markup=_build_stat_kb(poll.id), parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f"{POLL_STAT_REFRESH}:"))
async def cb_poll_stat_refresh(call: types.CallbackQuery) -> None:
    user_id = int(call.from_user.id)
    if not _is_admin(user_id):
        await call.answer("⛔ Нет доступа.", show_alert=True)
        return

    try:
        _, poll_id_str = call.data.split(":")
        poll_id = int(poll_id_str)
    except Exception:
        await call.answer("Некорректные данные.", show_alert=True)
        return

    poll = await get_poll(poll_id)
    if not poll or int(poll.admin_chat_id or 0) != user_id:
        await call.answer("⛔ Это не ваш опрос.", show_alert=True)
        return

    stats_text, total = build_stats_text(poll.question, poll.options or [], poll.votes or [])
    suffix = f"\n\n<b>Всего голосов:</b> {total}"
    try:
        await call.message.edit_text(stats_text + suffix, reply_markup=_build_stat_kb(poll.id), parse_mode="HTML")
        await call.answer("Статистика обновлена.")
    except Exception:
        await call.answer("Актуально.")
