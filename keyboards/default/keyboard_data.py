from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_data = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="номер автомата"),
            KeyboardButton(text="название (локация автомата)"),
        ],

    ],
    resize_keyboard=True,
    one_time_keyboard=True
)