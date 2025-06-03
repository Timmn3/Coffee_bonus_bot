from aiogram import Dispatcher
from .by_balance import PositiveBalance
from .private_chat import IsPrivate
from .groups_chat import IsGroup


# функция, которая выполняет установку кастомных фильтов
def setup(dp: Dispatcher):
    dp.filters_factory.bind(PositiveBalance)  # кастомный фильтр для проверки на позитивный баланс
    dp.filters_factory.bind(IsPrivate)  # кастомный фильтр на приватный чат с ботом
    dp.filters_factory.bind(IsGroup)  # кастомный фильтр на групповой чат
