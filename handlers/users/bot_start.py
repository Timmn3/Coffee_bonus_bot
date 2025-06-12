from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from filters import IsPrivate
from keyboards.default import kb_register_machine
from loader import dp
from utils.db_api.users_commands import add_user, select_user
from keyboards.default.keyboard_main import kb_main


@dp.message_handler(IsPrivate(), CommandStart())  # создаем message, который ловит команду /start
async def command_start(message: types.Message):  # создаем асинхронную функцию
    from utils.db_api.users_commands import (
        select_user, add_user, get_card_number_by_user_id,
        get_bonus_account_id, fetch_bonus_accounts_by_card,
        get_user_by_bonus_id
    )
    from utils.db_api.ie_commands import get_user_data
    from keyboards.default import kb_main, kb_register_machine
    from data.config import ADMIN_IE
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    args = message.get_args()  # например пользователь пишет /start 1233124 с айди которого пригласил

    try:
        user = await select_user(message.from_user.id)

        if user.status == 'active':
            await message.answer(f'Привет {user.tg_first_name}!\n', reply_markup=kb_main)

            # 👇 Если бонусный аккаунт еще не привязан — сверка
            bonus_id = await get_bonus_account_id(user.user_id)
            if bonus_id is None:
                card_numbers = await get_card_number_by_user_id(user.user_id)

                if card_numbers and card_numbers != '0':
                    cards = [c.strip() for c in card_numbers.split('\n') if c.strip()]
                    user_data = await get_user_data(ADMIN_IE)
                    token = user_data["token"]

                    all_items = []
                    for card in cards:
                        matches = await fetch_bonus_accounts_by_card(token, card)
                        all_items.extend(matches)

                    keyboard = InlineKeyboardMarkup(row_width=1)
                    options = 0
                    for item in all_items:
                        b_id = item["id"]
                        already = await get_user_by_bonus_id(b_id)
                        if already:
                            continue
                        bal = item["balance"] / 100
                        keyboard.add(InlineKeyboardButton(
                            text=f"{item['card_number']} — {bal:.2f} ₽",
                            callback_data=f"bind_bonus:{b_id}"
                        ))
                        options += 1

                    if options:
                        await message.answer(
                            "📌 Для корректной работы бота, пожалуйста, подтвердите свой бонусный баланс.\n"
                            "Сравните сумму бонусов с тем, что вы видите на терминале и выберите подходящий вариант:",
                            reply_markup=keyboard
                        )

        else:
            await message.answer(f'Здравствуйте, {user.tg_first_name}!\n')
            await message.answer(f'Пожалуйста, пройдите регистрацию', reply_markup=kb_register_machine)

    except Exception:
        await add_user(
            user_id=message.from_user.id,
            tg_first_name=message.from_user.first_name,
            tg_last_name=message.from_user.last_name,
            name=message.from_user.username,
            card_number='0',
            name_cards={},  # теперь есть
            phone_number='0',
            status='active',
            bonus={},  # JSON, не float
            number_ie=10,
            sms_status=False,
            bonus_account_id=None
        )

        await message.answer(f'Добро пожаловать, {message.from_user.first_name}!\n'
                             f'Для продолжения нажмите Регистрация', reply_markup=kb_register_machine)



