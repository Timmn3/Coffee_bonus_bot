from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel_change = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отменить")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)