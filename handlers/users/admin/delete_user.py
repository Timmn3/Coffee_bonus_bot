from filters.admins import Admins
from loader import dp
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from utils.db_api.users_commands import delete_user


class User(StatesGroup):
    id = State()


dp.message_handler(Admins(), text='/delete')


async def delete(message: types.Message):
    await message.answer(f'Введите id пользователя:')
    await User.id.set()


@dp.message_handler(state=User.id)
async def get_phone(message: types.Message, state: FSMContext):
    user_id = int(message.from_user.id)
    info = await delete_user(user_id)
    await message.answer(info)
