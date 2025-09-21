import asyncio
from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMIN_IE
from keyboards.inline import (
    POLL_ADD_OPTION_CALLBACK,
    POLL_CANCEL_CALLBACK,
    POLL_SEND_CALLBACK,
    build_poll_preview_kb,
    build_poll_vote_kb,
)
from loader import dp
from states import PollCreation
from utils.db_api.poll_commands import (
    create_poll,
    get_poll,
    increment_vote,
)
from utils.db_api.users_commands import get_all_user_ids


def _format_poll_message(question: str, options: List[str]) -> str:
    """Форматирование текста опроса для отправки пользователям."""
    lines = [f'<b>{question}</b>']
    lines.extend(f'{index}. {option}' for index, option in enumerate(options, start=1))
    return '\n'.join(lines)


@dp.message_handler(commands=['poll'], chat_id=ADMIN_IE)
async def poll_start(message: types.Message, state: FSMContext):
    """Старт создания опроса администратором."""
    await state.finish()
    await PollCreation.question.set()
    await state.update_data(options=[])
    await message.answer(
        'Введите текст вопроса для опроса.\n\n'
        'Отправьте «Отмена», чтобы прекратить создание опроса.'
    )


@dp.message_handler(state=PollCreation.question, chat_id=ADMIN_IE)
async def poll_set_question(message: types.Message, state: FSMContext):
    """Сохранить вопрос и перейти к вводу вариантов."""
    text = (message.text or '').strip()
    if text.lower() == 'отмена':
        await state.finish()
        await message.answer('Создание опроса отменено.')
        return

    if not text:
        await message.answer('Текст вопроса не может быть пустым. Попробуйте ещё раз.')
        return

    await state.update_data(question=text, options=[])
    await PollCreation.option.set()
    await message.answer(
        'Введите вариант ответа.\n'
        'Когда закончите — отправьте «Готово». Для отмены напишите «Отмена».'
    )


@dp.message_handler(state=PollCreation.option, chat_id=ADMIN_IE)
async def poll_collect_options(message: types.Message, state: FSMContext):
    """Сбор вариантов ответа."""
    text = (message.text or '').strip()
    lower_text = text.lower()

    if lower_text == 'отмена':
        await state.finish()
        await message.answer('Создание опроса отменено.')
        return

    if lower_text == 'готово':
        data = await state.get_data()
        options = data.get('options', [])

        if len(options) < 2:
            await message.answer('Добавьте как минимум два варианта ответа перед завершением.')
            return

        question = data.get('question')
        preview_text = _format_poll_message(question, options)
        await PollCreation.confirm.set()
        await message.answer(
            f'Предпросмотр опроса:\n\n{preview_text}',
            reply_markup=build_poll_preview_kb()
        )
        return

    if not text:
        await message.answer('Вариант ответа не может быть пустым. Введите другой вариант или «Отмена».')
        return

    data = await state.get_data()
    options = data.get('options', [])
    options.append(text)
    await state.update_data(options=options)
    await message.answer('Вариант добавлен. Можете добавить ещё или отправить «Готово».')


@dp.callback_query_handler(text=POLL_ADD_OPTION_CALLBACK, state=PollCreation.confirm, chat_id=ADMIN_IE)
async def poll_add_more(call: types.CallbackQuery, state: FSMContext):
    """Добавить ещё вариант после предпросмотра."""
    await call.answer()
    await call.message.edit_reply_markup()
    await PollCreation.option.set()
    await call.message.answer('Введите дополнительный вариант ответа или «Готово» для завершения.')


@dp.callback_query_handler(text=POLL_CANCEL_CALLBACK, state=PollCreation.confirm, chat_id=ADMIN_IE)
async def poll_cancel(call: types.CallbackQuery, state: FSMContext):
    """Отмена создания опроса."""
    await call.answer('Создание опроса отменено.')
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Опрос отменён.')


@dp.callback_query_handler(text=POLL_SEND_CALLBACK, state=PollCreation.confirm, chat_id=ADMIN_IE)
async def poll_send(call: types.CallbackQuery, state: FSMContext):
    """Сохранение опроса в БД и массовая рассылка пользователям (включая админов)."""
    data = await state.get_data()
    question = data.get('question')
    options = data.get('options', [])

    if not question or len(options) < 2:
        await call.answer('Недостаточно данных для отправки опроса.', show_alert=True)
        return

    creator_id = int(call.from_user.id)  # ← владелец опроса
    poll = await create_poll(question, options, admin_chat_id=creator_id)
    if poll is None:
        await call.answer('Не удалось сохранить опрос. Попробуйте позже.', show_alert=True)
        return

    poll_text = _format_poll_message(question, options)
    vote_keyboard = build_poll_vote_kb(poll.id, options)

    users = await get_all_user_ids()
    sent = 0
    for user_id in users:
        try:
            await dp.bot.send_message(chat_id=user_id, text=poll_text, reply_markup=vote_keyboard)
            sent += 1
            await asyncio.sleep(0.25)
        except Exception:
            continue

    await state.finish()
    try:
        await call.message.edit_reply_markup()
    except Exception:
        pass

    await call.answer('Опрос разослан!')
    await call.message.answer(f'Опрос отправлен {sent} пользователям из {len(users)}.')



@dp.callback_query_handler(lambda c: c.data and c.data.startswith('poll_vote:'))
async def poll_vote_handler(call: types.CallbackQuery):
    """
    Обработка нажатия варианта ответа пользователем.
    Формат callback_data: poll_vote:<poll_id>:<option_index>
    """
    try:
        parts = (call.data or '').split(':')
        if len(parts) != 3:
            await call.answer('Некорректные данные.', show_alert=True)
            return

        _, poll_id_str, option_idx_str = parts
        poll_id = int(poll_id_str)
        option_idx = int(option_idx_str)

        updated = await increment_vote(poll_id, option_idx)
        if updated is None:
            await call.answer('Ошибка сохранения голоса.', show_alert=True)
            return

        try:
            await call.message.edit_reply_markup()  # убираем кнопки после клика
        except Exception:
            pass

        await call.answer('Ваш голос засчитан!')
    except Exception:
        await call.answer('Произошла ошибка. Попробуйте ещё раз.', show_alert=False)
