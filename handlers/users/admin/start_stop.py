from aiogram import types
from loader import dp
from data.config import ADMIN_IE, CODER
from custom_parser.pars import start_processing, parsing_main, stop_processing

from utils.db_api.ie_commands import get_user_data


@dp.message_handler(text='/run', chat_id=CODER)
async def run(message: types.Message):
    users_data = await get_user_data(ADMIN_IE)
    await start_processing()
    await message.answer('Запущено!')
    # запустить процесс для всех пользователей
    await parsing_main(users_data)


@dp.message_handler(text='/stop', chat_id=CODER)
async def stop(message: types.Message):
    await stop_processing()
    await message.answer('Остановлено!')


