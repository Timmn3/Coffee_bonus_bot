from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мои бонусы"), KeyboardButton(text="Ваши карты")],
    ],
    resize_keyboard=True
)
