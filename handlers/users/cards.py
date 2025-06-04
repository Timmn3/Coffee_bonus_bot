""" Регистрация новой карты """

import re
from aiogram import types
from loader import dp
from utils.db_api.users_commands import get_card_number_by_user_id, update_card_number, remove_card_number
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


class Cards(StatesGroup):
    number = State()
    number_delete = State()


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
    await message.answer('Отменено')


@dp.message_handler(text='/cards')
async def cards_change(message: types.Message):
    user_id = int(message.from_user.id)
    cards = await get_card_number_by_user_id(user_id)

    if cards == '0':
        await message.answer('У Вас нет активных карт, для начала пройдите регистрацию /register')
    else:
        text = (
            f"👤 <b>ID:</b> <code>{user_id}</code>\n\n"
            f"💳 <b>Ваши карты:</b>\n{cards}\n\n"
            f"Выберите действие:"
        )
        await message.answer(text, reply_markup=kb_cards, parse_mode='HTML')



@dp.message_handler(text='Добавить карту')
async def register(message: types.Message):
    await message.answer('Введите номер карты, например: 22****3317')
    await Cards.number.set()


@dp.message_handler(state=Cards.number)
async def get_number(message: types.Message, state: FSMContext):
    number = message.text
    if number == "Oтмена":
        await state.finish()
        await message.answer('Отменено')
    else:
        user_id = int(message.from_user.id)

        if validate_number(number):
            # сохраняем номер карты в БД
            if await update_card_number(user_id, number):
                await message.answer(f'👍Отлично! Карта {number} зарегистрирована!')
                await state.finish()

        else:
            await message.answer('Некорректный ввод. Пример: 22****7192:', reply_markup=cards_cancel)


def validate_number(number):
    pattern = r'^\d{2}\*{4}\d{4}$'
    return re.match(pattern, number) is not None


@dp.message_handler(text='Удалить карту')
async def delete_card(message: types.Message):
    user_id = int(message.from_user.id)
    cards = await get_card_number_by_user_id(user_id)
    await message.answer(f'Ваши карты: \n{cards}\n'
                         f'Введите номер карты которую хотите удалить:')
    await Cards.number_delete.set()


@dp.message_handler(state=Cards.number_delete)
async def number_delete(message: types.Message, state: FSMContext):
    number = message.text
    if number == "Oтмена":
        await state.finish()
        await message.answer('Отменено')
    else:
        user_id = int(message.from_user.id)

        if validate_number(number):
            # удаляем номер карты в БД
            await remove_card_number(user_id, number)
            await state.finish()
            await message.answer(f'👍Отлично! Карта {number} удалена!')

        else:
            await message.answer('Некорректный ввод. Пример: 22****7192:', reply_markup=cards_cancel)
