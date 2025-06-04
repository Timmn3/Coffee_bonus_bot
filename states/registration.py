from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    number = State()
    name = State()  # новое состояние
    sms = State()
    phone = State()



class Accept(StatesGroup):
    user_id = State()
