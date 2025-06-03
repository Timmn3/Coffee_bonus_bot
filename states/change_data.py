from aiogram.dispatcher.filters.state import StatesGroup, State


class ChangeData(StatesGroup):
    number_machines = State()
    choice = State()
    new_value = State()
