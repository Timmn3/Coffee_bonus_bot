"""
Хендлер для просмотра бонусов пользователя.
Работает с таблицей 'cards' и API бонусных счетов.
"""
import aiohttp
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp
from utils.db_api.cards_commands import get_user_cards, get_card_by_number, update_bonus
from utils.db_api.bonus_commands import fetch_bonus_accounts_by_card, get_user_by_bonus_id, set_bonus_account_id
from utils.db_api.shemas.cards import Cards


@dp.message_handler(text=["/my_bonuses", "Мои бонусы"])
async def my_bonuses(message: types.Message):
    user_id = message.from_user.id
    cards = await get_user_cards(user_id)

    if not cards:
        await message.answer('У вас нет зарегистрированных карт.')
        return

    if len(cards) > 1:
        keyboard = InlineKeyboardMarkup(row_width=1)
        for card in cards:
            button_text = f"{card['card_number']} — {card['card_name']}"
            keyboard.add(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"card:{card['card_number']}"
                )
            )
        await message.answer("Выберите карту для просмотра бонусов:", reply_markup=keyboard)
    else:
        card_number = cards[0]['card_number']
        # Проверяем и привязываем bonus_account_id если нужно
        await check_and_bind_bonus_account(user_id, card_number, message)
        bonus = await get_bonus_api(card_number)
        await show_bonus_info(message, card_number, bonus)


@dp.callback_query_handler(lambda c: c.data.startswith('card:'))
async def process_callback_card(callback_query: types.CallbackQuery):
    selected_card = callback_query.data.split(':', 1)[1]
    user_id = callback_query.from_user.id

    # Проверяем и привязываем bonus_account_id если нужно
    await check_and_bind_bonus_account(user_id, selected_card, callback_query.message)

    bonus = await get_bonus_api(selected_card)
    text = (
        f'Карта: <code>{selected_card}</code>\n'
        f'Бонусы: {bonus} ₽'
    )

    await callback_query.message.edit_text(text, parse_mode='HTML')
    await callback_query.answer()


async def show_bonus_info(message: types.Message, card_number: str, bonus: float):
    await message.answer(
        f'У Вас {bonus} бонусов✅\n'
        f'<b>1 бонус = 1 рублю!</b>\n'
        f'Вы можете выбрать напиток и приложить карту как обычно к терминалу!\n'
        f'При достаточном наличии бонусов деньги не списываются и у Вас будет написано '
        f'<b>"бесплатная продажа"!</b>', parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data.startswith("bind_bonus:"))
async def bind_bonus_id(call: types.CallbackQuery):
    """
    Привязка бонусного аккаунта к пользователю.
    """
    try:
        _, bonus_id_str, card_number = call.data.split(":")
        bonus_id = int(bonus_id_str)
    except ValueError:
        await call.message.edit_text("⚠️ Ошибка в данных кнопки.")
        return

    user_id = call.from_user.id

    exists = await get_user_by_bonus_id(bonus_id)
    if exists and exists != user_id:
        await call.message.edit_text("❌ Этот бонусный аккаунт уже привязан к другому пользователю.")
        return

    success = await set_bonus_account_id(user_id, bonus_id, card_number)
    if success is True:
        await call.message.edit_text("✅ Бонусный аккаунт успешно привязан! Вы будете получать корректные бонусы.")
    elif success is False:
        await call.message.edit_text("⚠️ Не удалось привязать бонусный аккаунт. Попробуйте позже.")
    # Если уже привязано — ничего не пишем




async def get_bonus_api(card_number: str) -> float:
    """
    Получает актуальные бонусы по привязанному бонусному аккаунту этой карты.
    """
    from utils.db_api.ie_commands import get_user_data
    from data.config import ADMIN_IE
    from utils.db_api.cards_commands import get_card_by_number, update_bonus

    user_data = await get_user_data(ADMIN_IE)
    token = user_data.get("token")

    if not token:
        return 0.0

    # 1. Получаем карту и привязанный bonus_account_id
    card = await get_card_by_number(card_number)
    if not card or not card.bonus_account_id:
        return 0.0

    bonus_id = card.bonus_account_id

    # 2. Получаем список всех аккаунтов по карте
    matches = await fetch_bonus_accounts_by_card(token, card_number)
    if not matches:
        return 0.0

    # 3. Ищем нужный аккаунт по ID
    for item in matches:
        if item["id"] == bonus_id:
            balance = item["balance"] / 100
            await update_bonus(card.user_id, card_number, balance)
            return balance

    return 0.0




async def check_and_bind_bonus_account(user_id: int, card_number: str, message: types.Message):
    """
    Проверяет и привязывает bonus_account_id к карте, если он не привязан.

    :param user_id: ID пользователя Telegram
    :param card_number: Номер карты для проверки
    :param message: Объект сообщения для отправки ответов пользователю
    """
    from utils.db_api.ie_commands import get_user_data
    from data.config import ADMIN_IE

    # Проверяем, есть ли уже привязанный bonus_account_id к этой карте
    card = await Cards.query.where(
        (Cards.user_id == user_id) &
        (Cards.card_number == card_number)
    ).gino.first()

    if card and card.bonus_account_id:
        return True  # Уже привязан

    # Если нет - делаем запрос к API
    user_data = await get_user_data(ADMIN_IE)
    token = user_data.get("token")

    if not token:
        await message.answer("❌ Ошибка сервера")
        return False

    bonus_items = await fetch_bonus_accounts_by_card(token, card_number)

    if not bonus_items:
        await message.answer("🔸 Бонусный аккаунт не найден для этой карты.")
        return False

    # Фильтруем только непривязанные аккаунты
    available_accounts = []
    for item in bonus_items:
        exists = await get_user_by_bonus_id(item["id"])
        if not exists or exists == user_id:
            available_accounts.append(item)

    if not available_accounts:
        await message.answer("❗️ Все найденные бонусные ID уже привязаны к другим пользователям.")
        return False

    # Если найден только один аккаунт - привязываем автоматически
    if len(available_accounts) == 1:
        account = available_accounts[0]
        result = await set_bonus_account_id(user_id, account["id"], card_number)

        if result is True:
            await message.answer(f"✅ Бонусный аккаунт успешно привязан к карте {card_number}!")
        elif result is False:
            await message.answer("❌ Не удалось привязать бонусный аккаунт.")
        # если result is None — ничего не пишем

        return bool(result)

    # Если несколько аккаунтов - предлагаем выбор
    keyboard = InlineKeyboardMarkup(row_width=1)
    for account in available_accounts:
        balance = account["balance"] / 100
        keyboard.add(
            InlineKeyboardButton(
                text=f"{account['card_number']} — {balance:.2f} ₽",
                callback_data=f"bind_bonus:{account['id']}:{account['card_number']}"
            )
        )

    await message.answer(
        "🧾 Найдено несколько бонусных аккаунтов для этой карты.\n"
        "Пожалуйста, выберите подходящий:",
        reply_markup=keyboard
    )
    return False