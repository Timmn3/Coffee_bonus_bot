"""
Модуль для работы с таблицей 'users'.
Обновлено: вся работа с картами вынесена в модуль cards_commands.py.
"""

from loader import db
from utils.db_api.shemas.cards import Cards

from asyncpg import UniqueViolationError
from loguru import logger
from utils.db_api.shemas.users import Users


async def add_user(user_id: int, tg_first_name: str, tg_last_name: str, name: str,
                   phone_number: str, status: str, bonus: dict, number_ie: int, sms_status: bool):
    """
    Добавляет нового пользователя в базу данных Users, если его ещё нет.

    :param user_id: ID пользователя Telegram.
    :param tg_first_name: Имя пользователя Telegram.
    :param tg_last_name: Фамилия пользователя Telegram.
    :param name: Username Telegram.
    :param phone_number: Телефонный номер пользователя.
    :param status: Статус пользователя ('active', 'inactive').
    :param bonus: Словарь с бонусами (JSON поле).
    :param number_ie: Номер индивидуального предпринимателя.
    :param sms_status: Статус SMS уведомлений (True/False).
    :return: True если пользователь успешно добавлен, False если уже существует.
    """
    try:
        # Проверяем — есть ли уже такой пользователь
        existing_user = await Users.query.where(Users.user_id == user_id).gino.first()
        if existing_user:
            logger.warning(f"Пользователь с ID {user_id} уже существует в базе данных.")
            return False  # Пользователь уже есть — не добавляем повторно

        # Создаём нового пользователя
        user = Users(
            user_id=user_id,
            tg_first_name=tg_first_name,
            tg_last_name=tg_last_name,
            name=name,
            phone_number=phone_number,
            status=status,
            bonus=bonus,
            number_ie=number_ie,
            sms_status=sms_status
        )
        await user.create()
        logger.info(f"Пользователь с ID {user_id} успешно добавлен в базу данных.")
        return True  # Успешное добавление
    except UniqueViolationError:
        logger.exception('Ошибка при добавлении пользователя (уникальное ограничение нарушено)')
        return False
    except Exception as e:
        logger.exception(f'Неизвестная ошибка при добавлении пользователя: {e}')
        return False



async def get_all_user_ids():
    """Получить список всех Telegram ID пользователей."""
    try:
        user_ids = await db.select([Users.user_id]).gino.all()
        return [user_id[0] for user_id in user_ids]
    except Exception as e:
        logger.exception(f'Ошибка получения всех user_ids: {e}')
        return []


async def select_user(user_id):
    """Получить пользователя по его Telegram ID."""
    try:
        return await Users.query.where(Users.user_id == user_id).gino.first()
    except Exception as e:
        logger.exception(f'Ошибка при выборе пользователя: {e}')


async def update_phone_number(user_id: int, new_phone_number: str):
    """Обновить номер телефона пользователя."""
    try:
        await Users.update.values(phone_number=new_phone_number).where(Users.user_id == user_id).gino.status()
    except Exception as e:
        logger.exception(f'Ошибка при изменении номера телефона пользователя: {e}')


async def update_sms_status(user_id: int, new_sms_status: bool):
    """Обновить статус получения SMS уведомлений пользователя."""
    try:
        await Users.update.values(sms_status=new_sms_status).where(Users.user_id == user_id).gino.status()
    except Exception as e:
        logger.exception(f'Ошибка при изменении статуса SMS пользователя: {e}')


async def get_sms_status(user_id: int):
    """Получить статус SMS уведомлений пользователя."""
    try:
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        return user.sms_status if user else None
    except Exception as e:
        logger.exception(f'Ошибка при получении статуса SMS пользователя: {e}')
        return None


async def delete_user(user_id: int):
    """Удалить пользователя из базы данных."""
    try:
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            await user.delete()
            return f"Пользователь с ID {user_id} успешно удален."
        return f"Пользователь с ID {user_id} не найден."
    except Exception as e:
        logger.exception(f'Ошибка при удалении пользователя: {e}')


async def get_number_ie(user_id: int):
    """Получить номер ИП пользователя."""
    try:
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        return user.number_ie if user else None
    except Exception as e:
        logger.exception(f'Ошибка при получении значения number_ie: {e}')
        return None


async def count_users():
    """Получить общее количество пользователей."""
    try:
        return await db.func.count(Users.user_id).gino.scalar()
    except Exception as e:
        logger.exception(f'Ошибка при подсчете пользователей: {e}')
        return None


async def get_bonus_account_id(user_id: int):
    """
    Получить bonus_account_id из таблицы Cards по user_id.
    Если у пользователя несколько карт — вернуть список всех bonus_account_id.
    """
    try:
        cards = await Cards.query.where(Cards.user_id == user_id).gino.all()
        return [card.bonus_account_id for card in cards if card.bonus_account_id is not None]
    except Exception as e:
        from loguru import logger
        logger.exception(f'Ошибка при получении bonus_account_id для user_id={user_id}: {e}')
        return []


# Получить user_id по номеру карты
async def get_user_id_by_card_number(card_number: str):
    """
    Получить user_id по номеру карты из таблицы Cards.
    """
    try:
        card = await Cards.query.where(Cards.card_number == card_number).gino.first()
        if card:
            return card.user_id
        else:
            return None
    except Exception as e:
        from loguru import logger
        logger.exception(f'Ошибка при получении user_id по номеру карты: {e}')
        return None
