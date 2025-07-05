import os
from dotenv import load_dotenv

env_path = os.getenv("ENV_PATH", ".env")
load_dotenv(dotenv_path=env_path)



import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from custom_parser.pars import start_user
from data.config import REMINDER_DAY, REMINDER_HOUR, REMINDER_MINUTE, SEND_PAYMENT_REMINDER, LOG_PATH
from utils.notify_admins import send_monthly_payment_reminder



async def on_startup(dp):
    from loguru import logger
    logger.add(f"logs/{LOG_PATH}/loguru.log",
               format="{level: <8} {time:YYYY.MM.DD HH:mm:ss} {module}:{function}:{line} - {message}",
               level="DEBUG",
               rotation="5 MB",
               compression="zip")

    import filters
    filters.setup(dp)
    import middlewares
    middlewares.setup(dp)

    from loader import db
    from utils.db_api.db_gino import on_startup
    # logger.info('Подключение к PostgreSQL')
    await on_startup(db)

    # print('Удаление базы данных')
    # await db.gino.drop_all()

    # logger.info('создание таблиц')
    await db.gino.create_all()
    # logger.info('Готово')

    # импортирует функцию, которая отправляет сообщение о запуске бота всем администраторам
    from utils.notify_admins import on_startup_notufy
    # await on_startup_notufy(dp)

    # импортирует функцию, которая устанавливает команды бота
    from utils.set_bot_commands import set_default_commands
    await set_default_commands(dp)

    # выдает в консоль бот запущен
    logger.info("Бот запущен")
    asyncio.create_task(start_user())

    # Инициализация APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.start()

    # Ежемесячная задача:
    # Проверяем, нужно ли отправлять уведомления
    if SEND_PAYMENT_REMINDER:
        scheduler = AsyncIOScheduler()
        scheduler.start()

        scheduler.add_job(
            send_monthly_payment_reminder,
            trigger='cron',
            day=int(REMINDER_DAY),
            hour=int(REMINDER_HOUR),
            minute=int(REMINDER_MINUTE),
            misfire_grace_time=60,
            coalesce=True,
            max_instances=1
        )
        logger.info(f"Ежемесячное уведомление запланировано: {REMINDER_DAY} числа в {REMINDER_HOUR}:{REMINDER_MINUTE}")
    else:
        logger.info("Ежемесячное уведомление отключено через SEND_PAYMENT_REMINDER=False")


if __name__ == '__main__':
    from aiogram import executor  # импортируем executor для запуска поллинга
    from handlers import dp  # из хендлеров импортируем dp

    executor.start_polling(dp, on_startup=on_startup)

    # git push origin master
