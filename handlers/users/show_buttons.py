from aiogram import types
from filters import IsPrivate
from keyboards.default import kb_run_stop
from loader import dp


@dp.message_handler(text="/show_buttons")  # создаем message, который ловит команду
async def command_start(message: types.Message):  # создаем асинхронную функцию
    await message.answer('Нажмите RUN, чтобы запустить бота\n'
                         'Нажмите STOP, чтобы остановить бота\n'
                         'Нажмите RESTART, чтобы перезагрузить бота', reply_markup=kb_run_stop)
