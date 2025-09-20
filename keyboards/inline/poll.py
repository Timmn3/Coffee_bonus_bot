from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


POLL_SEND_CALLBACK = 'poll:send'
POLL_ADD_OPTION_CALLBACK = 'poll:add_option'
POLL_CANCEL_CALLBACK = 'poll:cancel'


def build_poll_preview_kb() -> InlineKeyboardMarkup:
    """Клавиатура предпросмотра опроса для администратора."""

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text='Разослать', callback_data=POLL_SEND_CALLBACK),
        InlineKeyboardButton(text='Добавить ещё', callback_data=POLL_ADD_OPTION_CALLBACK),
        InlineKeyboardButton(text='Отмена', callback_data=POLL_CANCEL_CALLBACK),
    )
    return keyboard


def build_poll_vote_kb(poll_id: int, options: Iterable[str]) -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответа для пользователей."""

    keyboard = InlineKeyboardMarkup(row_width=1)
    for index, option in enumerate(options):
        keyboard.add(
            InlineKeyboardButton(
                text=option,
                callback_data=f'poll_vote:{poll_id}:{index}'
            )
        )
    return keyboard
