from aiogram import types
from aiogram.utils.deep_linking import get_start_link
from loader import dp


@dp.message_handler(text="/ref")  # создаем хэндлер
async def command_ref(message: types.Message):  # создаем асинхронную функцию
    ref_link = await get_start_link(payload=message.from_user.id)
    await message.answer(ref_link)