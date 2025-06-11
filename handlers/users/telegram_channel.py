from aiogram import types
from data.config import CHANEL
from loader import dp


@dp.message_handler(text="/telegram_channel", )
async def telegram_channel(message: types.Message):
    await message.answer(f"Ссылка на наш Telegram канал: {CHANEL}")

