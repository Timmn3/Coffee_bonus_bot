"""
Хендлеры для просмотра статистики опросов администратором.

Функции:
- /poll_results — показать статистику последних N опросов
- Кнопка "Обновить" — обновить статистику конкретного опроса в текущем сообщении
- Кнопка "Закрыть" — удалить сообщение со статистикой
"""

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from data.config import ADMIN_IE
from loader import dp
from utils.db_api.shemas.polls import Polls
from utils.db_api.poll_commands import build_stats_text, get_poll


# Константы callback_data
POLL_STAT_REFRESH = "poll_stat_refresh"
POLL_STAT_CLOSE = "poll_stat_close"

def _build_stat_kb(poll_id: int) -> InlineKeyboardMarkup:
    """Собрать инлайн-клавиатуру для блока статистики опроса."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text="🔄 Обновить",
            callback_data=f"{POLL_STAT_REFRESH}:{poll_id}"
        ),
        InlineKeyboardButton(
            text="✖ Закрыть",
            callback_data=f"{POLL_STAT_CLOSE}:{poll_id}"
        ),
    )
    return kb


@dp.message_handler(commands=["poll_results"], chat_id=ADMIN_IE)
async def cmd_poll_results(message: types.Message, state: FSMContext) -> None:
    """Показать статистику последних опросов администратору."""
    # Сколько последних опросов показывать
    limit = 10

    polls = await Polls.query.order_by(Polls.id.desc()).limit(limit).gino.all()
    if not polls:
        await message.answer("Опросов ещё нет.")
        return

    # Отправляем по одному сообщению на опрос — наглядно и удобно обновлять
    for poll in polls:
        stats_text, total = build_stats_text(poll.question, poll.options or [], poll.votes or [])
        suffix = f"\n\n<b>Всего голосов:</b> {total}"
        await message.answer(
            stats_text + suffix,
            reply_markup=_build_stat_kb(poll.id),
            parse_mode="HTML"
        )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f"{POLL_STAT_REFRESH}:"),
                           chat_id=ADMIN_IE)
async def cb_poll_stat_refresh(call: types.CallbackQuery) -> None:
    """Обновить статистику конкретного опроса в текущем сообщении."""
    try:
        _, poll_id_str = call.data.split(":")
        poll_id = int(poll_id_str)
    except Exception:
        await call.answer("Некорректные данные.", show_alert=True)
        return

    poll = await get_poll(poll_id)
    if not poll:
        await call.answer("Опрос не найден.", show_alert=True)
        return

    stats_text, total = build_stats_text(poll.question, poll.options or [], poll.votes or [])
    suffix = f"\n\n<b>Всего голосов:</b> {total}"
    try:
        await call.message.edit_text(
            stats_text + suffix,
            reply_markup=_build_stat_kb(poll.id),
            parse_mode="HTML"
        )
        await call.answer("Статистика обновлена.")
    except Exception:
        # Если текст совпал, Telegram может ругнуться — просто ответим
        await call.answer("Актуально.")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f"{POLL_STAT_CLOSE}:"),
                           chat_id=ADMIN_IE)
async def cb_poll_stat_close(call: types.CallbackQuery) -> None:
    """Закрыть (удалить) сообщение со статистикой."""
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.answer()
