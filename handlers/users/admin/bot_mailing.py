from asyncio import sleep
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from filters import IsPrivate
from loader import dp
from utils.db_api import ie_commands as commands
from states import bot_mailing

from data.config import ADMIN_IE
from utils.db_api.users_commands import get_user_id_by_card_number, get_all_user_ids


@dp.message_handler(IsPrivate(), text='/test', chat_id=ADMIN_IE)
async def start_mailing(message: types.Message):
    await message.answer(f'test')
    print(await get_user_id_by_card_number('22****7194'))


@dp.message_handler(IsPrivate(), text='/mailing', chat_id=ADMIN_IE)
async def start_mailing(message: types.Message):
    await message.answer(f'Введите текст рассылки:')
    await bot_mailing.text.set()


@dp.message_handler(IsPrivate(), state=bot_mailing.text, chat_id=ADMIN_IE)
async def mailing_text(message: types.Message, state: FSMContext):
    answer = message.text
    murkup = InlineKeyboardMarkup(row_width=2,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='Добавить фото', callback_data='add_foto'),
                                          InlineKeyboardButton(text='Отправить', callback_data='next'),
                                          InlineKeyboardButton(text='Отменить', callback_data='quit')
                                      ]
                                  ])
    await state.update_data(text=answer)
    await message.answer(text=answer, reply_markup=murkup)  # чтобы отобразилась клавиатура
    await bot_mailing.state.set()


@dp.callback_query_handler(text='next', state=bot_mailing.state, chat_id=ADMIN_IE)
async def start(call: types.CallbackQuery, state: FSMContext):
    users = await get_all_user_ids()
    data = await state.get_data()  # создаем переменную data из которой достаем ответы пользователя
    text = data.get('text')
    await state.finish()
    await call.message.delete()
    for user in users:
        try:
            await dp.bot.send_message(chat_id=user, text=text)
            await sleep(0.25)  # 4 сообщения в секунду
        except Exception:
            pass
    await call.message.answer('Рассылка выполнена!')


@dp.callback_query_handler(text='add_foto', state=bot_mailing.state, chat_id=ADMIN_IE)
async def add_foto(call: types.CallbackQuery):
    await call.message.answer('Пришлите фото')
    await bot_mailing.photo.set()


@dp.message_handler(IsPrivate(), state=bot_mailing.photo, content_types=types.ContentType.PHOTO, chat_id=ADMIN_IE)
async def mailing_text(message: types.Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    data = await state.get_data()  # создаем переменную data из которой достаем ответы пользователя
    text = data.get('text')
    photo = data.get('photo')
    murkup = InlineKeyboardMarkup(row_width=2,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='Отправить', callback_data='next'),
                                          InlineKeyboardButton(text='Отменить', callback_data='quit')
                                      ]
                                  ])
    await message.answer_photo(photo=photo, caption=text, reply_markup=murkup)


@dp.callback_query_handler(text='next', state=bot_mailing.photo, chat_id=ADMIN_IE)
async def start(call: types.CallbackQuery, state: FSMContext):
    users = await get_all_user_ids()
    data = await state.get_data()  # создаем переменную data из которой достаем ответы пользователя
    text = data.get('text')
    photo = data.get('photo')
    await state.finish()
    await call.message.delete()
    for user in users:
        try:
            await dp.bot.send_photo(chat_id=user, photo=photo, caption=text)
            await sleep(0.25)  # 4 сообщения в секунду
        except Exception:
            pass
    await call.message.answer('Рассылка выполнена')


@dp.message_handler(IsPrivate(), state=bot_mailing.photo, chat_id=ADMIN_IE)
async def no_photo(message: types.Message):
    murkup = InlineKeyboardMarkup(row_width=2,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='Отменить', callback_data='quit'),

                                      ]
                                  ])
    await message.answer('Пришли мне фотографию', reply_markup=murkup)


@dp.callback_query_handler(text='quit', state=[bot_mailing.text, bot_mailing.photo, bot_mailing.state], chat_id=ADMIN_IE)
async def quit(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer('Рассылка отменена')
