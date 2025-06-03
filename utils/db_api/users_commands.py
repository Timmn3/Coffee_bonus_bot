from asyncpg import UniqueViolationError
from loguru import logger

from utils.db_api.db_gino import db
from utils.db_api.shemas.users import Users


async def add_user(user_id: int, tg_first_name: str, tg_last_name: str, name: str, card_number: str, phone_number: str,
                   status: str, bonus: float, number_ie: int, sms_status: bool):
    try:
        user = Users(user_id=user_id, tg_first_name=tg_first_name, tg_last_name=tg_last_name,
                     name=name, card_number=card_number, phone_number=phone_number,
                     status=status, bonus=bonus, number_ie=number_ie, sms_status=sms_status)
        await user.create()
    except UniqueViolationError:
        logger.exception('Ошибка при добавлении пользователя')


async def get_all_user_ids():
    """ Получение списка всех ID пользователей """
    try:
        user_ids = await db.select([Users.user_id]).gino.all()
        return [user_id[0] for user_id in user_ids]
    except Exception as e:
        logger.exception(f'Ошибка получения всех user_ids: {e}')
        return []


async def select_user(user_id):
    """ Выбрать пользователя"""
    try:
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        return user
    except Exception as e:
        logger.exception(f'Ошибка при выборе пользователя: {e}')


async def update_card_number(user_id: int, new_card_number: str):
    """ Изменить номер карты пользователя """
    try:
        # Проверяем, существует ли пользователь
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            # Получаем текущий номер карты
            current_card_number = user.card_number
            # Если текущий номер равен "0", заменяем его новым номером
            if current_card_number == "0":
                current_card_number = new_card_number
            else:
                # Иначе, добавляем новый номер с новой строки
                current_card_number = f"{current_card_number}\n{new_card_number}"

            # Обновляем номер карты
            await Users.update.values(card_number=current_card_number).where(Users.user_id == user_id).gino.status()
            return True
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить номер карты.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении номера карты пользователя: {e}')


async def update_phone_number(user_id: int, new_phone_number: str):
    """ Изменить номер телефона пользователя """
    try:
        # Проверяем, существует ли пользователь
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            # Если пользователь существует, обновляем номер телефона
            await Users.update.values(phone_number=new_phone_number).where(Users.user_id == user_id).gino.status()

        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить номер телефона.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении номера телефона пользователя: {e}')


async def update_sms_status(user_id: int, new_sms_status: bool):
    """ Изменить статус SMS пользователя """
    try:
        # Проверяем, существует ли пользователь
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            # Если пользователь существует, обновляем статус SMS
            await Users.update.values(sms_status=new_sms_status).where(Users.user_id == user_id).gino.status()

        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить статус SMS.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении статуса SMS пользователя: {e}')


async def get_sms_status(user_id: int):
    """ Получить статус SMS пользователя """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем статус SMS
            return user.sms_status
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить статус SMS.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении статуса SMS пользователя: {e}')
        return None  # or raise an exception if you prefer


async def delete_user(user_id: int):
    """ Удалить пользователя из базы данных """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Удаляем пользователя
            await user.delete()

            info = f"Пользователь с ID {user_id} успешно удален."
        else:
            info = f"Пользователь с ID {user_id} не найден."

        return info
    except Exception as e:
        logger.exception(f'Ошибка при удалении пользователя: {e}')


async def get_number_ie(user_id: int):
    """ Получить значение number_ie для пользователя """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем значение number_ie
            return user.number_ie
        else:
            # logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить значение number_ie.")
            return None
    except Exception as e:
        logger.exception(f'Ошибка при получении значения number_ie для пользователя: {e}')
        return None  # or raise an exception if you prefer


async def get_user_id_by_card_number(card: str):
    """ Получить user_id по номеру карты """
    try:
        # Ищем пользователя по номеру карты
        user = await Users.query.where(Users.card_number.contains(card)).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем user_id
            return user.user_id
        else:
            # logger.warning(f"Пользователь с номером карты {card} не найден. Невозможно получить user_id.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении user_id по номеру карты: {e}')
        return None  # or raise an exception if you prefer


async def update_bonus(user_id: int, new_bonus: float):
    """ Изменить значение бонусов пользователя """
    try:
        # Проверяем, существует ли пользователь
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            # Если пользователь существует, обновляем значение бонусов
            await Users.update.values(bonus=new_bonus).where(Users.user_id == user_id).gino.status()
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить значение бонусов.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении значения бонусов пользователя: {e}')


async def get_bonus(user_id: int):
    """ Получить значение бонусов пользователя """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем значение бонусов
            return user.bonus
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить значение бонусов.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении значения бонусов пользователя: {e}')
        return None  # or raise an exception if you prefer


async def count_users():
    try:
        count = await db.func.count(Users.user_id).gino.scalar()
        return count
    except Exception as e:
        logger.exception(f'Ошибка при подсчете пользователей: {e}')
        return None


async def get_card_number_by_user_id(user_id: int):
    """ Получить номер карты по user_id """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем номер карты
            return user.card_number
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить номер карты.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении номера карты по user_id: {e}')
        return None  # or raise an exception if you prefer


async def remove_card_number(user_id: int, partial_card_number: str):
    """ Удалить номер карты по частичному номеру """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Получаем текущий номер карты
            current_card_number = user.card_number

            # Проверяем, содержится ли указанный частичный номер в текущем номере карты
            if partial_card_number in current_card_number:
                # Удаляем указанный частичный номер из текущего номера карты
                updated_card_number = "\n".join(
                    line for line in current_card_number.split("\n") if partial_card_number not in line)

                # Обновляем номер карты
                await Users.update.values(card_number=updated_card_number).where(Users.user_id == user_id).gino.status()

                info = f"Частичный номер карты {partial_card_number} успешно удален у пользователя с ID {user_id}."
            else:
                info = f"Частичный номер карты {partial_card_number} не найден у пользователя с ID {user_id}."

            return info
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно удалить частичный номер карты.")
            return f"Пользователь с ID {user_id} не найден."
    except Exception as e:
        logger.exception(f'Ошибка при удалении частичного номера карты: {e}')
        return f'Ошибка при удалении частичного номера карты: {e}'
