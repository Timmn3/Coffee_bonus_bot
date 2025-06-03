from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    number = State()
    sms = State()
    phone = State()


class Accept(StatesGroup):
    user_id = State()
