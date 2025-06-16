import asyncio
import logging
import json
from datetime import datetime

from utils.db_api.shemas.cards import Cards
# Импортируй свои модели
from utils.db_api.shemas.users import Users
from loguru import logger


async def migrate_user_cards():
    """
    Переносит данные о картах из поля JSON/TEXT в отдельную таблицу cards.
    """
    logger.info("🚀 Начинаем миграцию карт...")
    users = await Users.query.gino.all()

    for user in users:
        try:
            if not user.card_number or user.card_number == '0':
                continue

            # Разбираем номера карт
            card_numbers = [c.strip() for c in user.card_number.split('\n') if c.strip()]
            name_cards = user.name_cards or {}

            for card in card_numbers:
                card_name = name_cards.get(card, '')  # Получаем имя карты из JSON

                # Создаем запись в таблице cards
                await Cards.create(
                    user_id=user.user_id,
                    card_number=card,
                    card_name=card_name,
                    bonus_account_id=None,
                    created_at=datetime.now(),
                    active=True,
                    bonus=0
                )
                logger.debug(f"Сохранена карта {card} для пользователя {user.user_id}")

        except Exception as e:
            logger.exception(f"Ошибка при обработке пользователя {user.user_id}:")
            continue

    logger.info("✅ Миграция завершена")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrate_user_cards())