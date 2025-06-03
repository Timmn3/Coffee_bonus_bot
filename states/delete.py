from aiogram.dispatcher.filters.state import StatesGroup, State


class Delete(StatesGroup):
    number_machines = State()
