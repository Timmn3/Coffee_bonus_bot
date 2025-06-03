from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_register_machine = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Регистрация"),
        ],

    ],
    resize_keyboard=True,
    one_time_keyboard=True
)