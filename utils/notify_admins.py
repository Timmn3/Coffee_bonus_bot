import logging

from aiogram import Dispatcher

from data.config import CODER
from loguru import logger

from utils.db_api.users_commands import count_users


async def on_startup_notufy(dp: Dispatcher):
    try:
        text = 'Бот запущен'
        await dp.bot.send_message(chat_id=CODER, text=text)
    except Exception as err:
        logging.exception(err)


# отправляет сообщение админам о новом зарегистрированном пользователе
async def new_user_registration(dp: Dispatcher, username):
    count = await count_users()
    try:
        await dp.bot.send_message(chat_id=CODER, text=f'✅В бонусной программе зарегистрирован новый пользователь: '
                                                      f'username: @{username}\n'
                                                      f'🚹Всего пользователей: <b>{count}</b>')
    except Exception as err:
        logger.exception(err)


async def send_admins(dp: Dispatcher, text):
    try:
        await dp.bot.send_message(chat_id=CODER, text=text)
    except Exception as err:
        logger.exception(err)