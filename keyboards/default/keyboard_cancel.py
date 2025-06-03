from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel_registration = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отменить регистрацию")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)