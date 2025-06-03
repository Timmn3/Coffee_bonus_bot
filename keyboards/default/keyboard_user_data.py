from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_user_data = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="email"),
            KeyboardButton(text="пароль"),
        ],
        [
            KeyboardButton(text="время отчета"),
            KeyboardButton(text="добавить пользователя"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)