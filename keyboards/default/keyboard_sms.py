from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_sms = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="да"),
            KeyboardButton(text="нет"),

        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True

)


kb_sms_cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отключить уведомления"),
            KeyboardButton(text="Отмена"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)