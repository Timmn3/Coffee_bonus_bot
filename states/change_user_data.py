from aiogram.dispatcher.filters.state import StatesGroup, State


class ChangeUserData(StatesGroup):
    email = State()
    password = State()
    choice = State()
    new_value = State()
