from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_restart = ReplyKeyboardMarkup(
    keyboard=[
        [

            KeyboardButton(text="restart"),

        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)