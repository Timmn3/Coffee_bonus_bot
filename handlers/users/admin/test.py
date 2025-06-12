from data.config import CODER
from filters.admins import Admins
from loader import dp, bot
from aiogram import types

from utils.db_api.users_commands import get_bonus_api
from utils.migration.migrate_cards import migrate_user_cards


@dp.message_handler(Admins(), text='/test')
async def test(message: types.Message):
    await bot.send_message(chat_id=CODER, text="Запрос...")
    card_number = "22****3317"
    balance = await get_bonus_api(card_number)
    await bot.send_message(chat_id=CODER, text=f"Баланс: {balance}")

@dp.message_handler(Admins(), text='/migrat')
async def test(message: types.Message):
    await bot.send_message(chat_id=CODER, text="Миграция")
    await migrate_user_cards()

