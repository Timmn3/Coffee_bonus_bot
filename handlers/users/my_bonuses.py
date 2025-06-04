from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp
from utils.db_api.users_commands import get_bonus, get_card_number_by_user_id, get_name_cards
from keyboards.inline.ikb_cards import get_card_selection_keyboard


@dp.message_handler(text="/my_bonuses")
async def my_bonuses(message: types.Message):
    user_id = message.from_user.id
    card_numbers = await get_card_number_by_user_id(user_id)
    bonus = await get_bonus(user_id, card_numbers)
    if not card_numbers or card_numbers == '0':
        await message.answer('У вас нет зарегистрированных карт.')
        return

    # Разбиваем на список, если есть несколько карт
    card_list = [card.strip() for card in card_numbers.split('\n') if card.strip()]

    if len(card_list) > 1:
        name_cards = await get_name_cards(user_id)

        keyboard = InlineKeyboardMarkup(row_width=1)
        for card in card_list:
            name = name_cards.get(card, '—')
            button_text = f"{card} — {name}"
            keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"card:{card}"))

        await message.answer("Выберите карту для просмотра бонусов:", reply_markup=keyboard)
    else:
        if bonus:
            await message.answer(f'У Вас {bonus} бонусов✅\n'
                                 f'<b>1 бонус = 1 рублю!</b>\n'
                                 f'Вы можете выбрать напиток и приложить карту как обычно к терминалу!\n'
                                 f'При достаточном наличии бонусов деньги не списываются и у Вас будет написано '
                                 f'<b>"бесплатная продажа"!</b>')
        else:
            await message.answer('Совершите оплату в кофеаппарате, чтобы появились бонусы!')



@dp.callback_query_handler(lambda c: c.data.startswith('card:'))
async def process_callback_card(callback_query: types.CallbackQuery):
    selected_card = callback_query.data.split(':', 1)[1]
    user_id = callback_query.from_user.id

    bonus = await get_bonus(user_id, selected_card)  # <-- теперь передаем карту
    text = (
        f'Карта: <code>{selected_card}</code>\n'
        f'Бонусы: {bonus} ₽'
    )

    await callback_query.message.edit_text(text, parse_mode='HTML')
    await callback_query.answer()

@dp.message_handler(text="Мои бонусы")
async def handle_bonuses_button(message: types.Message):
    await my_bonuses(message)

