from aiogram.dispatcher.filters.state import State, StatesGroup


class PollCreation(StatesGroup):
    """Состояния для создания опроса администратором."""

    question = State()
    option = State()
    confirm = State()
