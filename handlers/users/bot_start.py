"""
Хендлер для команды /start.
Обеспечивает регистрацию пользователя и проверку его бонусных карт.
"""

from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from filters import IsPrivate
from loader import dp
from utils.db_api.bonus_commands import get_user_by_bonus_id
from utils.db_api.users_commands import select_user, add_user
from utils.db_api.ie_commands import get_user_data
from data.config import ADMIN_IE
from keyboards.default import kb_main, kb_register_machine
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger


@dp.message_handler(IsPrivate(), CommandStart())
async def command_start(message: types.Message):
    """
    Обработчик команды /start.
    Проверяет наличие пользователя в БД, предлагает регистрацию новым пользователям,
    проверяет наличие бонусных карт для старых пользователей.
    """
    args = message.get_args()  # Аргументы после /start (например реферальный ID)

    try:
        user = await select_user(message.from_user.id)

        if user is None:
            # Если пользователь не найден, создаем нового
            await add_user(
                user_id=message.from_user.id,
                tg_first_name=message.from_user.first_name,
                tg_last_name=message.from_user.last_name,
                name=message.from_user.username,
                phone_number='0',
                status='active',
                bonus={},
                number_ie=10,
                sms_status=False
            )
            await message.answer(
                f'Добро пожаловать, {message.from_user.first_name}!\n'
                f'Для продолжения нажмите "Регистрация"',
                reply_markup=kb_register_machine
            )
            return

        if user.status == 'active':
            await message.answer(f'Привет {user.tg_first_name}!\n', reply_markup=kb_main)

            # 🔍 Проверяем привязку бонусного аккаунта
            from utils.db_api.cards_commands import get_user_cards
            from utils.db_api.bonus_commands import fetch_bonus_accounts_by_card

            user_cards = await get_user_cards(user.user_id)

            if user_cards:
                user_data = await get_user_data(ADMIN_IE)
                token = user_data["token"]

                all_items = []
                for card in user_cards:
                    matches = await fetch_bonus_accounts_by_card(token, card['card_number'])
                    all_items.extend(matches)

                keyboard = InlineKeyboardMarkup(row_width=1)
                options = 0
                for item in all_items:
                    b_id = item["id"]
                    already = await get_user_by_bonus_id(b_id)
                    if already:
                        continue
                    bal = item["balance"] / 100
                    keyboard.add(
                        InlineKeyboardButton(
                            text=f"{item['card_number']} — {bal:.2f} ₽",
                            callback_data=f"bind_bonus:{b_id}"
                        )
                    )
                    options += 1

                if options > 0:
                    from utils.db_api.cards_commands import get_card_by_number
                    unlinked_cards = []
                    for item in all_items:
                        card = await get_card_by_number(item["card_number"])
                        if card and not card.bonus_account_id:
                            unlinked_cards.append(item["card_number"])

                    if unlinked_cards:
                        await message.answer(
                            "📌 Для корректной работы бота, пожалуйста, подтвердите свой бонусный баланс.\n"
                            "Сравните сумму бонусов с тем, что вы видите на терминале и выберите подходящий вариант:",
                            reply_markup=keyboard
                        )

        else:
            await message.answer(f'Здравствуйте, {user.tg_first_name}!\n')
            await message.answer(f'Пожалуйста, пройдите регистрацию', reply_markup=kb_register_machine)

    except Exception as e:
        logger.exception(f"Ошибка в обработчике /start: {e}")
        await message.answer("Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")
