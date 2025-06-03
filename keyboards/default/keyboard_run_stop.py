from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_run_stop = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="run"),
            KeyboardButton(text="stop"),
            KeyboardButton(text="restart"),

        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)