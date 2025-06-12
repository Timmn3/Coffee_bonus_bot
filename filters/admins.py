from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import CODER


class Admins(BoundFilter):  # проверка админа
    async def check(self, message: types.Message):
        if message.from_user.id == int(CODER):
            return True
        else:
            return False
