from aiogram import types

from data.config import USER_HELP
from loader import dp

@dp.message_handler(text="/help")
async def command_help(message: types.Message):
    await message.answer(f'Если у Вас есть вопросы, напишите мне: {USER_HELP}')
