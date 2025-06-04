""" Регистрация новой карты """
import html
import re
from aiogram import types

from keyboards.default import kb_main
from loader import dp
from utils.db_api.users_commands import get_card_number_by_user_id, update_card_number, remove_card_number
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from utils.db_api.users_commands import (
    get_name_cards,
    set_card_name,
    rename_card_number
)
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
    cards = await get_card_number_by_user_id(user_id)
    names = await get_name_cards(user_id)

    if cards == '0':
        await message.answer('У Вас нет активных карт, для начала пройдите регистрацию /register')
    else:
        lines = []
        for card in cards.split('\n'):
            if card.strip():
                name = names.get(card.strip(), '—')
                lines.append(f"{card.strip()} — <i>{name}</i>")
        text = "<b>Ваши карты:</b>\n" + "\n".join(lines)

        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Удалить карту"),
                 KeyboardButton(text="Добавить карту")],
                [KeyboardButton(text="✏️ Редактировать карту")],
                [KeyboardButton(text="Oтмена")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(text, reply_markup=kb)

@dp.message_handler(text='✏️ Редактировать карту')
async def edit_card_start(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    cards_raw = await get_card_number_by_user_id(user_id)
    name_cards = await get_name_cards(user_id)

    card_list = [c.strip() for c in cards_raw.split('\n') if c.strip()]
    if not card_list:
        await message.answer("У вас нет карт для редактирования.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for card in card_list:
        name = name_cards.get(card, '—')
        button_text = f"{card} — {name}"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"edit_card:{card}"))

    await message.answer("Выберите карту, которую хотите отредактировать:", reply_markup=keyboard)
    await state.finish()  # сбрасываем состояние на случай старых FSM

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
    await state.update_data(new_card=card)  # важно: new_card = тот же номер, если имя меняем
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
    name = message.text.strip()
    data = await state.get_data()
    old_card = data['old_card']
    new_card = data['new_card']
    user_id = message.from_user.id

    await remove_card_number(user_id, old_card)
    await update_card_number(user_id, new_card)
    await rename_card_number(user_id, old_card, new_card)
    await set_card_name(user_id, new_card, name)

    await state.finish()
    await message.answer(f'Карта обновлена:\n{new_card} — <i>{html.escape(name)}</i>')


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
    else:
        user_id = int(message.from_user.id)

        if validate_number(number):
            # сохраняем номер карты в БД
            if await update_card_number(user_id, number):
                await state.update_data(card_number=number)  # сохраняем номер карты
                await message.answer(
                    "Введите имя для этой карты (например: 'Кофейный автомат'):")
                await Cards.new_name.set()


        else:
            await message.answer('Некорректный ввод. Пример: 22****7192:', reply_markup=cards_cancel)

@dp.message_handler(state=Cards.new_name)
async def set_card_name_after_add(message: types.Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    card = data.get("card_number")
    user_id = message.from_user.id

    if card:
        await set_card_name(user_id, card, name)
        await message.answer(f'👍 Карта <code>{card}</code> сохранена как <i>{name}</i>!', parse_mode='HTML')
    else:
        await message.answer('Произошла ошибка. Попробуйте снова через /cards')
    await state.finish()


def validate_number(number):
    pattern = r'^\d{2}\*{4}\d{4}$'
    return re.match(pattern, number) is not None


@dp.message_handler(text='Удалить карту')
async def delete_card(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    cards_raw = await get_card_number_by_user_id(user_id)
    name_cards = await get_name_cards(user_id)

    card_list = [c.strip() for c in cards_raw.split('\n') if c.strip()]
    if not card_list:
        await message.answer("У вас нет активных карт.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for card in card_list:
        name = name_cards.get(card, '—')
        button_text = f"{card} — {name}"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"delete_card:{card}"))

    await message.answer("Выберите карту, которую хотите удалить:", reply_markup=keyboard)
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('delete_card:'))
async def handle_delete_card_callback(call: types.CallbackQuery):
    card = call.data.split(':', 1)[1]
    user_id = int(call.from_user.id)

    await remove_card_number(user_id, card)
    await call.message.answer(f'👍 Карта <code>{card}</code> удалена!')
    await call.answer()


@dp.message_handler(state=Cards.number_delete)
async def number_delete(message: types.Message, state: FSMContext):
    number = message.text
    if number == "Oтмена":
        await state.finish()
        await message.answer('Отменено', reply_markup=kb_main)
    else:
        user_id = int(message.from_user.id)

        if validate_number(number):
            # удаляем номер карты в БД
            await remove_card_number(user_id, number)
            await state.finish()
            await message.answer(f'👍Отлично! Карта {number} удалена!')

        else:
            await message.answer('Некорректный ввод. Пример: 22****7192:', reply_markup=cards_cancel)


@dp.message_handler(text="Ваши карты")
async def handle_cards_button(message: types.Message):
    await cards_change(message)
