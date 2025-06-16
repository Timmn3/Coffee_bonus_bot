"""
Модуль для работы с таблицей 'cards' в базе данных.
Содержит функции для получения, добавления, удаления и обновления информации о картах пользователя.
"""

from utils.db_api.shemas.cards import Cards
from loguru import logger


async def get_card_by_number(card_number: str):
    """
    Получить карту по её номеру.

    :param card_number: Номер карты в формате строки (например '22****7192').
    :return: Объект Cards или None, если карта не найдена.
    """
    return await Cards.query.where(Cards.card_number == card_number).gino.first()


async def update_bonus(user_id: int, card_number: str, new_bonus: float):
    """
    Обновить бонус на карте пользователя.

    :param user_id: ID пользователя Telegram.
    :param card_number: Номер карты.
    :param new_bonus: Новое значение бонусов.
    """
    try:
        card = await Cards.query.where(
            (Cards.user_id == user_id) &
            (Cards.card_number == card_number)
        ).gino.first()

        if card:
            await card.update(bonus=new_bonus).apply()
            logger.debug(f"Бонус для карты {card_number} обновлен на {new_bonus} ₽")
        else:
            logger.warning(f"Карта {card_number} для пользователя {user_id} не найдена.")

    except Exception as e:
        logger.exception(f"Ошибка при обновлении бонусов: {e}")


async def get_user_cards(user_id: int):
    """
    Получить все карты пользователя.

    :param user_id: ID пользователя Telegram.
    :return: Список словарей с полями 'card_number' и 'card_name'.
    """
    try:
        cards = await Cards.query.where(Cards.user_id == user_id).gino.all()
        return [{"card_number": c.card_number, "card_name": c.card_name} for c in cards]
    except Exception as e:
        logger.exception(f"Ошибка при получении карт пользователя {user_id}: {e}")
        return []


async def add_user_card(user_id: int, card_number: str, card_name: str = ""):
    """
    Добавить новую карту для пользователя.

    :param user_id: ID пользователя Telegram.
    :param card_number: Номер карты.
    :param card_name: Название карты (по умолчанию пустая строка).
    :return: True если успешно, иначе False.
    """
    try:
        await Cards.create(
            user_id=user_id,
            card_number=card_number,
            card_name=card_name
        )
        logger.debug(f"Добавлена карта {card_number} для пользователя {user_id}")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при добавлении карты: {e}")
        return False


async def delete_user_card(user_id: int, card_number: str):
    """
    Удалить карту пользователя по номеру карты.

    :param user_id: ID пользователя Telegram.
    :param card_number: Номер карты.
    :return: True если успешно удалено, иначе False.
    """
    try:
        card = await Cards.query.where(
            (Cards.user_id == user_id) &
            (Cards.card_number == card_number)
        ).gino.first()

        if card:
            await card.delete()
            logger.debug(f"Удалена карта {card_number} для пользователя {user_id}")
            return True
        else:
            logger.warning(f"Карта {card_number} для пользователя {user_id} не найдена.")
            return False

    except Exception as e:
        logger.exception(f"Ошибка при удалении карты: {e}")
        return False


async def rename_card(user_id: int, old_number: str, new_name: str):
    """
    Переименовать карту пользователя.

    :param user_id: ID пользователя Telegram.
    :param old_number: Старый номер карты.
    :param new_name: Новое имя карты.
    :return: True если успешно переименовано, иначе False.
    """
    try:
        card = await Cards.query.where(
            (Cards.user_id == user_id) &
            (Cards.card_number == old_number)
        ).gino.first()

        if card:
            await card.update(card_name=new_name).apply()
            logger.debug(f"Карта {old_number} переименована в {new_name} для пользователя {user_id}")
            return True
        else:
            logger.warning(f"Карта {old_number} для пользователя {user_id} не найдена.")
            return False

    except Exception as e:
        logger.exception(f"Ошибка при переименовании карты: {e}")
        return False
