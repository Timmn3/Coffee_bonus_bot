import aiohttp
from utils.db_api.shemas.cards import Cards


async def fetch_bonus_accounts_by_card(token: str, card_number: str):
    """
    Получить список бонусных аккаунтов по номеру карты из внешнего API.
    """
    url = "https://api.vendista.ru:99/bonusaccounts"
    async with aiohttp.ClientSession() as session:
        params = {
            "token": token,
            "OrderByColumn": 3,
            "OrderDesc": 'true',
            "FilterText": card_number
        }
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("items", [])
            return []


async def get_user_by_bonus_id(bonus_account_id: int):
    """
    Получить пользователя по бонусному аккаунту.
    """
    card = await Cards.query.where(Cards.bonus_account_id == bonus_account_id).gino.first()
    return card.user_id if card else None


async def set_bonus_account_id(user_id: int, bonus_account_id: int, card_number: str):
    from .cards_commands import Cards
    from loguru import logger

    logger.debug(f"Пытаемся привязать bonus_account_id={bonus_account_id} к карте {card_number} (user_id={user_id})")

    # 1. Проверка: не привязан ли бонус уже к какой-либо карте
    bonus_used = await Cards.query.where(Cards.bonus_account_id == bonus_account_id).gino.first()
    if bonus_used:
        logger.warning(f"bonus_account_id={bonus_account_id} уже привязан к user_id={bonus_used.user_id}, card={bonus_used.card_number}")
        return False

    # 2. Ищем указанную карту
    card = await Cards.query.where(
        (Cards.user_id == user_id) & (Cards.card_number == card_number)
    ).gino.first()

    if not card:
        logger.error(f"Карта {card_number} не найдена для user_id={user_id}")
        return False

    # 3. Проверка: уже привязана?
    if card.bonus_account_id == bonus_account_id:
        logger.debug(f"bonus_account_id={bonus_account_id} уже привязан к этой карте {card_number}")
        return None

    if card.bonus_account_id is not None:
        logger.warning(f"Карта {card_number} уже имеет другой привязанный бонус: {card.bonus_account_id}")
        return False

    # 4. Привязка
    await card.update(bonus_account_id=bonus_account_id).apply()
    logger.success(f"Привязка успешна: bonus_account_id={bonus_account_id} → карта {card_number} (user_id={user_id})")
    return True





async def get_card_name_by_number(user_id: int, card_number: str) -> str:
    """
    Получает имя карты из таблицы Cards по user_id и card_number.

    :param user_id: ID пользователя Telegram.
    :param card_number: Номер карты.
    :return: Название карты или 'Без названия', если карта не найдена.
    """
    card = await Cards.query.where(
        (Cards.user_id == user_id) &
        (Cards.card_number == card_number)
    ).gino.first()

    return card.card_name if card else "Без названия"