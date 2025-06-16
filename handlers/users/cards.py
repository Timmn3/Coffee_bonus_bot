""" Регистрация новой карты """
import html
import re
from aiogram import types

from handlers.users.bot_registration import validate_number
from keyboards.default import kb_main
from loader import dp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from utils.db_api.cards_commands import get_user_cards, add_user_card, delete_user_card, rename_card
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Cards(StatesGroup):
    number = State()
    number_delete = State()
    edit_select = State()
    edit_number = State()
    edit_name = State()
    new_name = State()


kb_cards = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Удалить карту"),
            KeyboardButton(text="Добавить карту"),
            KeyboardButton(text="Oтмена"),
        ],

    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


cards_cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Oтмена"),
        ],

    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


@dp.message_handler(text='Oтмена')
async def cast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Отменено', reply_markup=kb_main)


@dp.message_handler(text='/cards')
async def cards_change(message: types.Message):
    user_id = int(message.from_user.id)
    cards = await get_user_cards(user_id)

    if not cards:
        await message.answer('У Вас нет активных карт, для начала пройдите регистрацию /register')
        return

    lines = []
    for card in cards:
        name = card['card_name'] or 'Имя карты'
        lines.append(f"{card['card_number']} — <i>{name}</i>")

    text = "<b>Ваши карты:</b>\n" + "\n".join(lines)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Удалить карту"), KeyboardButton(text="Добавить карту")],
            [KeyboardButton(text="✏️ Редактировать карту")],
            [KeyboardButton(text="Oтмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(text, reply_markup=kb, parse_mode='HTML')

@dp.message_handler(text='✏️ Редактировать карту')
async def edit_card_start(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    cards = await get_user_cards(user_id)

    if not cards:
        await message.answer("У вас нет карт для редактирования.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for card in cards:
        name = card['card_name'] or '—'
        button_text = f"{card['card_number']} — {name}"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"edit_card:{card['card_number']}"))

    await message.answer("Выберите карту, которую хотите отредактировать:", reply_markup=keyboard)
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('edit_card:'))
async def handle_edit_card_callback(call: types.CallbackQuery, state: FSMContext):
    card = call.data.split(':', 1)[1]
    await state.update_data(old_card=card)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✏️ Изменить номер", callback_data="edit_number"),
        InlineKeyboardButton(text="📝 Изменить имя", callback_data="edit_name")
    )

    await call.message.answer(f"Что вы хотите изменить для карты <code>{card}</code>?", reply_markup=keyboard)
    await call.answer()

@dp.callback_query_handler(text="edit_number")
async def edit_number_selected(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    card = data.get("old_card")
    await call.message.answer(f"Введите новый номер для карты <code>{card}</code>:", reply_markup=cards_cancel)
    await Cards.edit_number.set()
    await call.answer()


@dp.callback_query_handler(text="edit_name")
async def edit_name_selected(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    card = data.get("old_card")
    await call.message.answer(f"Введите новое имя для карты <code>{card}</code>:", reply_markup=cards_cancel)
    await Cards.edit_name.set()
    await state.update_data(new_card=card)
    await call.answer()


@dp.message_handler(state=Cards.edit_number)
async def edit_card_number(message: types.Message, state: FSMContext):
    new_number = message.text.strip()
    if validate_number(new_number):
        await state.update_data(new_card=new_number)
        await message.answer("Теперь введите новое имя для карты:")
        await Cards.edit_name.set()
    else:
        await message.answer('Неверный формат. Пример: 22****7192', reply_markup=cards_cancel)


@dp.message_handler(state=Cards.edit_name)
async def edit_card_name(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    data = await state.get_data()
    old_card = data['old_card']
    user_id = message.from_user.id

    if await rename_card(user_id, old_card, new_name):
        await message.answer(f'👍 Имя карты <code>{old_card}</code> изменено на <i>{new_name}</i>', parse_mode='HTML')
    else:
        await message.answer('Ошибка при изменении имени карты.')

    await state.finish()


@dp.message_handler(text='Добавить карту')
async def register(message: types.Message):
    await message.answer('Введите номер карты, например: <code>22****3317</code>', parse_mode='HTML')
    await Cards.number.set()


@dp.message_handler(state=Cards.number)
async def get_number(message: types.Message, state: FSMContext):
    number = message.text
    if number == "Oтмена":
        await state.finish()
        await message.answer('Отменено', reply_markup=kb_main)
        return

    user_id = int(message.from_user.id)

    if validate_number(number):
        await state.update_data(card_number=number)
        await message.answer("Введите имя для этой карты:")
        await Cards.new_name.set()
    else:
        await message.answer('Некорректный ввод. Пример: 22****7192:', reply_markup=cards_cancel)

@dp.message_handler(state=Cards.new_name)
async def set_card_name_after_add(message: types.Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    card = data.get("card_number")
    user_id = message.from_user.id

    if not card:
        await message.answer('Произошла ошибка. Попробуйте снова через /cards')
        await state.finish()
        return

    # Сохраняем карту
    success = await add_user_card(user_id, card, name)
    if not success:
        await message.answer('Не удалось сохранить карту.')
        await state.finish()
        return

    await message.answer(f'👍 Карта <code>{card}</code> сохранена как <i>{name}</i>!', parse_mode='HTML')

    # 🔄 Попытка привязки бонусного ID
    from utils.db_api.ie_commands import get_user_data
    from data.config import ADMIN_IE
    from utils.db_api.bonus_commands import fetch_bonus_accounts_by_card, get_user_by_bonus_id, set_bonus_account_id
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    user_data = await get_user_data(ADMIN_IE)
    token = user_data.get("token")
    if not token:
        await state.finish()
        return

    bonus_items = await fetch_bonus_accounts_by_card(token, card)
    if not bonus_items:
        await message.answer("🔸 Бонусный аккаунт не найден для этой карты.")
        await state.finish()
        return

    # Оставляем только не привязанные или к этому пользователю
    available_accounts = [
        b for b in bonus_items if (await get_user_by_bonus_id(b["id"])) in [None, user_id]
    ]

    if not available_accounts:
        await message.answer("❗️ Все найденные бонусные ID уже привязаны к другим пользователям.")
        await state.finish()
        return

    if len(available_accounts) == 1:
        b = available_accounts[0]
        result = await set_bonus_account_id(user_id, b["id"], card)
        if result is True:
            await message.answer(f"✅ Бонусный аккаунт автоматически привязан к карте {card}!")
        elif result is False:
            await message.answer("❌ Не удалось привязать бонусный аккаунт.")
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        for b in available_accounts:
            balance = b["balance"] / 100
            keyboard.add(
                InlineKeyboardButton(
                    text=f"{b['card_number']} — {balance:.2f} ₽",
                    callback_data=f"bind_bonus:{b['id']}:{b['card_number']}"
                )
            )
        await message.answer(
            "🧾 Найдено несколько бонусных аккаунтов для этой карты.\n"
            "Пожалуйста, выберите подходящий:",
            reply_markup=keyboard
        )

    await state.finish()


@dp.message_handler(text='Удалить карту')
async def delete_card(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    cards = await get_user_cards(user_id)

    if not cards:
        await message.answer("У вас нет активных карт.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for card in cards:
        name = card['card_name'] or '—'
        button_text = f"{card['card_number']} — {name}"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"delete_card:{card['card_number']}"))

    await message.answer("Выберите карту, которую хотите удалить:", reply_markup=keyboard)
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('delete_card:'))
async def handle_delete_card_callback(call: types.CallbackQuery):
    card = call.data.split(':', 1)[1]
    user_id = int(call.from_user.id)

    if await delete_user_card(user_id, card):
        await call.message.answer(f'👍 Карта <code>{card}</code> удалена!', parse_mode='HTML')
    else:
        await call.message.answer('Ошибка при удалении карты.')

    await call.answer()



@dp.message_handler(text="Ваши карты")
async def handle_cards_button(message: types.Message):
    await cards_change(message)
