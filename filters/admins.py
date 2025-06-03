from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import CODER


class Admins(BoundFilter):  # проверка админа
    async def check(self, message: types.Message):
        # id пользователя
        user = int(message.from_user.id)
        if user == CODER:
            return True
        else:
            return False
