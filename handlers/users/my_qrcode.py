from aiogram import types
from loader import dp, bot
from utils.misc.qr_code import create_qr_code
import os


async def send_qr_code(user_id: int):
    qr_code = await create_qr_code(user_id)
    file_path = f"qr_{user_id}.png"
    qr_code.save(file_path)

    # Отправляем файл пользователю
    with open(file_path, 'rb') as photo:
        await bot.send_photo(user_id, photo)

    # Удаляем файл после отправки
    os.remove(file_path)


@dp.message_handler(text="/qr")
async def command_ref(message: types.Message):
    user_id = message.from_user.id
    await send_qr_code(user_id)
