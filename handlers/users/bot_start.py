from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from filters import IsPrivate
from keyboards.default import kb_register_machine
from loader import dp
from utils.db_api.users_commands import add_user, select_user
from keyboards.default.keyboard_main import kb_main


@dp.message_handler(IsPrivate(), CommandStart())  # создаем message, который ловит команду /start
async def command_start(message: types.Message):  # создаем асинхронную функцию

    args = message.get_args()  # например пользователь пишет /start 1233124 с айди которого пригласил


    try:
        user = await select_user(message.from_user.id)
        if user.status == 'active':
            await message.answer(f'Привет {user.tg_first_name}!\n', reply_markup=kb_main)
        else:
            await message.answer(f'Здравствуйте, {user.tg_first_name}!\n')

            await message.answer(f'Пожалуйста, пройдите регистрацию', reply_markup=kb_register_machine)

    except Exception:
        await add_user(user_id=message.from_user.id,
                       tg_first_name=message.from_user.first_name,
                       tg_last_name=message.from_user.last_name,
                       name=message.from_user.username,
                       card_number='0',
                       phone_number='0',
                       status='active',
                       bonus=0,
                       number_ie=10,
                       sms_status=False)

        await message.answer(f'Добро пожаловать, {message.from_user.first_name}!\n'
                             f'Для продолжения нажмите Регистрация', reply_markup=kb_register_machine)


