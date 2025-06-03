
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from keyboards.default.keyboard_sms import kb_sms_cancel
from loader import dp
from utils.db_api.ie_commands import get_sms_status_ie
from utils.db_api.users_commands import update_sms_status, update_phone_number, get_sms_status, get_number_ie
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class SMS(StatesGroup):
    number = State()



kb_cancel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


@dp.message_handler(text='Отмена')
async def cast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Отменено')


@dp.message_handler(Command('sms_notifications'))
async def sms_notifications(message: types.Message):
    user_id_ie = await get_number_ie(message.from_user.id)
    # смотрим подключена ли СМС уведомление в кофейне
    if not await get_sms_status_ie(user_id_ie):
        await message.answer('Услуга СМС информирования отключена на этих кофейных аппаратах')
    else:
        # смотрим подключена ли СМС уведомление
        if await get_sms_status(message.from_user.id):
            await message.answer('Вы хотите отключить СМС уведомление?', reply_markup=kb_sms_cancel)
        else:
            await message.answer('На какой номер Вы хотели бы получать СМС уведомления?')
            await message.answer('Введите номер телефона в формате 89886654411:', reply_markup=kb_cancel)
            await SMS.number.set()


@dp.message_handler(text='Отключить уведомления')
async def disable_notifications(message: types.Message):
    await update_sms_status(message.from_user.id, False)
    await message.answer('СМС уведомления отключены \n'
                         'Для повторного подключения выберете в меню пункт "СМС уведомления"')


@dp.message_handler(state=SMS.number)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if phone == 'Отмена':
        await state.finish()
        await message.answer('Отменено')
    else:
        user_id = int(message.from_user.id)
        if validate_phone(phone):
            # сохраняем номер в БД
            await update_phone_number(user_id, phone)
            await update_sms_status(user_id, True)
            await message.answer(f'Отлично! Теперь Вы будете получать уведомления по СМС на номер {phone}\n'
                                 f'Если вы не хотите получать СМС, в меню выберите пункт "СМС уведомления"')
            await state.finish()
        else:
            await message.answer('Некорректный ввод. Пример: 89886654411:',
                                 reply_markup=kb_cancel)


def validate_phone(phone):
    pattern = r'^89\d{9}$'
    return re.match(pattern, phone) is not None


@dp.message_handler(Command('change_phone'))
async def change_phone(message: types.Message):
    """ Изменить номер телефона"""
    await message.answer('Введите номер телефона в формате 89886654411:', reply_markup=kb_cancel)
    await SMS.number.set()
