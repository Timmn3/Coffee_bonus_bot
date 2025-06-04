import asyncio
import aiohttp
from datetime import datetime
from loguru import logger

from data.config import CODER, ADMIN_IE
from utils.db_api.ie_commands import change_last_time, get_last_time, get_user_data
from utils.db_api.users_commands import get_user_id_by_card_number, update_bonus
from loader import bot

API_URL = "https://api.vendista.ru:99/bonusaccounts"


def format_now() -> str:
    """Текущее время в формате строки."""
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


async def parse_iso_datetime(iso_str: str) -> str:
    """Преобразует ISO-время из API в формат DD.MM.YYYY HH:MM:SS"""
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%d.%m.%Y %H:%M:%S")


async def should_update(sale_time: str, db_time: str) -> bool:
    """Сравнивает время продажи и последнее сохранённое время."""
    t1 = datetime.strptime(sale_time, '%d.%m.%Y %H:%M:%S')
    t2 = datetime.strptime(db_time, '%d.%m.%Y %H:%M:%S')
    return t1 > t2


async def format_bonus(bonus: int) -> str:
    """Форматирует бонусы в строку с пробелами и запятой."""
    return f"{bonus / 100:,.2f}".replace(",", " ").replace(".", ",")


class BonusUpdater:
    def __init__(self, token: str):
        self.token = token

    async def fetch_data(self) -> list[dict]:
        """Получает бонусные данные из API."""
        async with aiohttp.ClientSession() as session:
            params = {
                "token": self.token,
                "OrderByColumn": 3,
                "OrderDesc": 'true'
            }
            async with session.get(API_URL, params=params) as resp:
                if resp.status == 200:
                    return (await resp.json())["items"]
                logger.error(f"API request failed with status {resp.status}")
                return []

    async def process_user_data(self, user_data: dict):
        user_id = user_data["user_id"]


        try:
            while True:
                now_str = format_now()
                last_check = await get_last_time(user_id)
                # last_check = "02.06.2025 00:38:33"

                items = await self.fetch_data()

                for item in items:
                    card_number = item["card_number"]
                    balance = item["balance"]
                    sale_time_raw = item["last_change_time"]

                    sale_time = await parse_iso_datetime(sale_time_raw)

                    if await should_update(sale_time, last_check):
                        user = await get_user_id_by_card_number(card_number)
                        if user:
                            await update_bonus(user, card_number, balance / 100)
                            bonus = await format_bonus(balance)
                            msg = f"💳 Карта: {card_number}\nБонусы: {bonus} ₽"
                            # print(msg)
                            await bot.send_message(user, msg)
                            # await bot.send_message(CODER, f"{user}\n{msg}")

                await change_last_time(user_id, now_str)
                await asyncio.sleep(30)

        except Exception:
            logger.exception("Ошибка при обновлении бонусных данных")
            await change_last_time(user_id, format_now())
            await bot.send_message(CODER, "❌ Ошибка извлечения бонусных данных")


async def start_user():
    user_data = await get_user_data(ADMIN_IE)
    updater = BonusUpdater(token=user_data["token"])
    try:
        await updater.process_user_data(user_data)
    except asyncio.CancelledError:
        pass  # Обработка отмены
