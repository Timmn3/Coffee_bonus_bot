# -*- coding: utf-8 -*-
"""
Установка команд бота с раздельным меню:
- Пользователи (scope=Default): базовые команды
- Админы (scope=Chat для каждого admin_id): админские команды
"""

from aiogram import types
from data.config import ADMIN_IE, CODER


async def set_default_commands(dp):
    # --- Команды для всех пользователей (по умолчанию) ---
    user_commands = [
        types.BotCommand('start', 'Старт'),
        types.BotCommand('register', 'Регистрация'),
        types.BotCommand('cards', 'Ваши карты'),
        types.BotCommand('my_bonuses', 'Мои бонусы'),
        types.BotCommand('telegram_channel', 'Наш телеграм-канал'),
        types.BotCommand('help', 'Помощь'),
    ]
    await dp.bot.set_my_commands(user_commands, scope=types.BotCommandScopeDefault())

    # --- Команды для админов (отдельное меню в их личках) ---
    admin_commands = [
        types.BotCommand('start', 'Старт'),
        types.BotCommand('mailing', 'Массовая рассылка'),
        types.BotCommand('poll', 'Создать опрос'),
        types.BotCommand('poll_results', 'Результаты опроса'),
        types.BotCommand('show_buttons', 'Кнопки управления (run/stop)'),
        types.BotCommand('help', 'Помощь'),
    ]

    admin_ids = {int(ADMIN_IE), int(CODER)}
    for admin_id in admin_ids:
        # В приватном чате chat_id == user_id администратора
        await dp.bot.set_my_commands(
            admin_commands,
            scope=types.BotCommandScopeChat(chat_id=admin_id)
        )
