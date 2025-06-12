import re
from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api.ie_commands import get_user_data
from utils.db_api.users_commands import set_card_name, get_user_by_bonus_id, fetch_bonus_accounts_by_card
from data.config import ADMIN_IE
from keyboards.default import cancel_registration, kb_main
from loader import dp
from states import Registration
from utils.db_api.users_commands import update_card_number, update_phone_number, update_sms_status, get_number_ie, \
    get_card_number_by_user_id
from utils.notify_admins import new_user_registration
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@dp.message_handler(text='Отменить регистрацию')
async def cast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Отменено', reply_markup=kb_main)


@dp.message_handler(text=['Регистрация', '/register'])
async def register(message: types.Message):
    user_id = int(message.from_user.id)
    cards = await get_card_number_by_user_id(user_id)
    if cards == '0':
        await message.answer('Для понимания какой картой Вы оплачиваете кофе, введите первые две цифры своей карты, '
                             'потом 4 звездочки и последние четыре цифры карты, \nнапример: 22****7192')
        await message.answer('Номер карты:', reply_markup=cancel_registration)
        await Registration.number.set()
    else:
        await message.answer(f'Вы зарегистрированы!\nВаши карты: \n{cards}\n'
                             f'Если Вы хотите добавить или удалить карту выберите в меню пункт /cards')


@dp.message_handler(state=Registration.number)
async def get_number(message: types.Message, state: FSMContext):
    number = message.text
    if number == "Отменить регистрацию":
        await state.finish()
        await message.answer('Отменено', reply_markup=kb_main)
    else:
        user_id = int(message.from_user.id)

        if validate_number(number):
            await state.update_data(card_number=number)  # сохраняем номер во временное состояние
            await message.answer("Введите имя для этой карты (например: 'Рабочая', 'Личная', 'Кофейный автомат у входа'):")
            await Registration.name.set()
        else:
            await message.answer('Некорректный ввод. Пример: 22****7192:', reply_markup=cancel_registration)

@dp.message_handler(state=Registration.name)
async def get_card_name_reg(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    name = message.text.strip()
    data = await state.get_data()
    number = data.get("card_number")

    if not validate_number(number):
        await message.answer('Ошибка: номер карты недействителен, попробуйте снова с /register')
        await state.finish()
        return

    await update_card_number(user_id, number)
    await set_card_name(user_id, number, name)

    await state.finish()

    from utils.db_api.ie_commands import get_user_data
    from utils.db_api.users_commands import fetch_bonus_accounts_by_card, get_user_by_bonus_id
    from data.config import ADMIN_IE

    user_data = await get_user_data(ADMIN_IE)
    token = user_data["token"]

    bonus_items = await fetch_bonus_accounts_by_card(token, number)
    if not bonus_items:
        await message.answer(
            "🔸 Бонусы пока не обнаружены.\n\n"
            "✅ Совершите покупку на кассе или терминале, чтобы бонусная карта активировалась.\n"
            "После этого вы сможете воспользоваться всеми возможностями бота."
        )
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    options = 0
    for item in bonus_items:
        bonus_id = item["id"]
        already_used = await get_user_by_bonus_id(bonus_id)
        if already_used:
            continue
        balance = item["balance"] / 100
        keyboard.add(
            InlineKeyboardButton(
                text=f"{item['card_number']} — {balance:.2f} ₽",
                callback_data=f"bind_bonus:{bonus_id}"
            )
        )
        options += 1

    if options:
        await message.answer(
            "🧾 Мы нашли несколько бонусных карт, подходящих под ваш номер.\n"
            "Пожалуйста, выберите свою, сверяя баланс с терминалом оплаты:",
            reply_markup=keyboard
        )
    else:
        await message.answer("❗️Все найденные бонусные ID уже привязаны к другим пользователям.")


def validate_number(number):
    pattern = r'^\d{2}\*\*\*\*\d{4}$'
    return re.match(pattern, number) is not None


@dp.message_handler(text='да')
async def register(message: types.Message):
    await message.answer('На какой номер Вы хотели бы получать СМС уведомления?')
    await message.answer('Введите номер телефона в формате 89886654411:', reply_markup=cancel_registration)
    await Registration.phone.set()


@dp.message_handler(state=Registration.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if phone == "Отменить регистрацию":
        await state.finish()
        await message.answer('Отменено', reply_markup=kb_main)
    else:
        user_id = int(message.from_user.id)
        if validate_phone(phone):
            # сохраняем номер карты в БД
            await update_phone_number(user_id, phone)
            await update_sms_status(user_id, True)
            await message.answer('Отлично! Теперь Вы будете получать уведомления в telegram и по СМС\n'
                                 'Если вы не хотите получать СМС, в меню выберите пункт "СМС уведомления"')
            # отправляем админам нового пользователя
            await new_user_registration(dp=dp, username=message.from_user.username)
            await state.finish()
        else:
            await message.answer('Некорректный ввод. Пример: 89886654411:',
                                 reply_markup=cancel_registration)


def validate_phone(phone):
    pattern = r'^89\d{9}$'
    return re.match(pattern, phone) is not None


@dp.message_handler(text='нет')
async def register(message: types.Message, state: FSMContext):
    await message.answer('👍Отлично! Регистрация завершена, теперь вы будете получать уведомления о балансе '
                         'бонусов в telegram боте!📲')
    # отправляем админам нового пользователя
    await new_user_registration(dp=dp, username=message.from_user.username)
    await state.finish()
