import logging

from aiogram import Dispatcher, types
from aiogram.utils.exceptions import TelegramAPIError

from data.config import CODER, ADMIN_IE, PAYMENT_CARD
from loguru import logger

from loader import dp
from utils.db_api.users_commands import count_users


async def on_startup_notufy(dp: Dispatcher):
    try:
        text = 'Бот запущен'
        await dp.bot.send_message(chat_id=CODER, text=text)
    except Exception as err:
        logging.exception(err)


# отправляет сообщение админам о новом зарегистрированном пользователе
async def new_user_registration(dp: Dispatcher, username):
    count = await count_users()
    try:
        message = (
            f'✅В бонусной программе зарегистрирован новый пользователь: \n'
            f'username: @{username}\n'
            f'🚹Всего пользователей: <b>{count}</b>'
        )

        for admin_id in [CODER, ADMIN_IE]:
            await dp.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')

    except Exception as err:
        logger.exception(err)


async def send_admins(dp: Dispatcher, text):
    try:
        await dp.bot.send_message(chat_id=CODER, text=text)
    except Exception as err:
        logger.exception(err)


async def send_monthly_payment_reminder():
    try:
        ikb_payment = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton("Оплата внесена", callback_data="payment_made")
        )
        await dp.bot.send_message(
            chat_id=ADMIN_IE,
            text=f"🔔 Напоминание: необходимо внести абонентскую плату 1000 ₽ на карту:\n"
                 f"💳 Номер карты: `{PAYMENT_CARD}`\n"
                 f"Завтра будет последний день для оплаты.",
            reply_markup=ikb_payment,
            parse_mode="Markdown"
        )
        logger.info("Ежемесячное уведомление о платеже отправлено администратору.")
    except Exception as e:
        logger.exception(f"Ошибка при отправке уведомления администратору: {e}")

# Флаг для отслеживания ожидания чека
waiting_for_receipt = {}

# Обработчик нажатия на кнопку "Оплата внесена"
@dp.callback_query_handler(text="payment_made")
async def handle_payment_made(callback_query: types.CallbackQuery):
    try:
        # Убираем клавиатуру и просим отправить чек
        await callback_query.message.edit_reply_markup()
        await callback_query.message.answer("📸 Пожалуйста, отправьте чек об оплате.")
        waiting_for_receipt[callback_query.from_user.id] = True  # Включаем ожидание чека
        await callback_query.answer()
    except TelegramAPIError as e:
        logger.error(f"Ошибка при обработке нажатия кнопки 'Оплата внесена': {e}")


# Обработчик получения фото или файла (чека)
@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT])
async def handle_receipt(message: types.Message):
    user_id = message.from_user.id

    if user_id in waiting_for_receipt and waiting_for_receipt[user_id]:
        try:
            # Отключаем флаг ожидания
            waiting_for_receipt[user_id] = False

            # Пересылаем чек админу (CODER)
            await message.forward(chat_id=CODER)

            # Подтверждение пользователю
            await message.answer("✅ Чек успешно отправлен. Оплата будет проверена.")
        except TelegramAPIError as e:
            logger.error(f"Ошибка при пересылке чека: {e}")
            await message.answer("❌ Произошла ошибка при отправке чека. Попробуйте ещё раз.")
    else:
        # Если не ожидаем чек — игнорируем
        pass