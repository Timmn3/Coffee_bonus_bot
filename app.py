import os
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from custom_parser.pars import start_user
from data.config import REMINDER_DAY, REMINDER_HOUR, REMINDER_MINUTE, SEND_PAYMENT_REMINDER, LOG_PATH
from utils.notify_admins import send_monthly_payment_reminder

# Загружаем переменные окружения
env_path = os.getenv("ENV_PATH", ".env")
load_dotenv(dotenv_path=env_path)

# Глобальная переменная под задачу парсера
parser_task = None


async def run_parser():
    """
    Запускает парсер, а через час перезапускает его.
    """
    global parser_task

    while True:
        # Отменяем предыдущую задачу, если она ещё жива
        if parser_task and not parser_task.done():
            parser_task.cancel()
            try:
                await parser_task
            except asyncio.CancelledError:
                pass

        # Запускаем новую задачу парсера
        parser_task = asyncio.create_task(start_user())

        # Ждём 1 час (3600 секунд)
        await asyncio.sleep(3600)


async def on_startup(dp):
    from loguru import logger

    # Настройка логгирования
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
    from utils.db_api.db_gino import on_startup as db_on_startup

    await db_on_startup(db)
    await db.gino.create_all()

    from utils.notify_admins import on_startup_notufy
    await on_startup_notufy(dp)

    from utils.set_bot_commands import set_default_commands
    await set_default_commands(dp)

    logger.info("Бот запущен")

    # Запуск парсера с перезапуском каждый час
    asyncio.create_task(run_parser())

    # Инициализация планировщика
    scheduler = AsyncIOScheduler()
    scheduler.start()

    if SEND_PAYMENT_REMINDER:
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
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)


    #git push origin master

