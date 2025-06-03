from aiogram.dispatcher.filters import BoundFilter
from aiogram import types

from loader import dp
from utils.db_api import ie_commands as commands

class PositiveBalance(BoundFilter):  # проверка достаточный ли баланс
    async def check(self, message: types.Message):
        # все пользователи из БД c позитивным балансом
        users = str(await commands.select_all_users_big_balance())
        # id пользователя
        user = str(message.from_user.id)

        if user in users:
            return True
        else:
            await dp.bot.send_message(chat_id=user, text='❗️Пополните баланс❗️')
            return False