import asyncio
import logging
import json
from datetime import datetime

from utils.db_api.shemas.cards import Cards
# Импортируй свои модели
from utils.db_api.shemas.users import Users


# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_user_cards():
    """
    Переносит данные о картах из поля JSON/TEXT в отдельную таблицу cards.
    """
    logger.info("🚀 Начинаем миграцию карт...")
    users = await Users.query.gino.all()

    for user in users:
        try:
            if not user.card_number or user.card_number == '0':
                logger.debug(f"Пользователь {user.user_id} не имеет карт")
                continue

            # Разбираем номера карт
            card_numbers = [c.strip() for c in user.card_number.split('\n') if c.strip()]
            name_cards = user.name_cards or {}

            logger.info(f"У пользователя {user.user_id} найдено {len(card_numbers)} карт")

            for card in card_numbers:
                card_name = name_cards.get(card, '')  # Получаем имя карты из JSON
                bonus_account_id = user.bonus_account_id if card == user.card_number else None

                # Создаем запись в таблице cards
                await Cards.create(
                    user_id=user.user_id,
                    card_number=card,
                    card_name=card_name,
                    bonus_account_id=bonus_account_id,
                    created_at=datetime.now(),
                    active=True
                )
                logger.debug(f"Сохранена карта {card} для пользователя {user.user_id}")

        except Exception as e:
            logger.exception(f"Ошибка при обработке пользователя {user.user_id}: {e}")
            continue

    logger.info("✅ Миграция завершена")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(migrate_user_cards())