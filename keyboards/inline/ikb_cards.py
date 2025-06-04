from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_card_selection_keyboard(cards: list):
    """
    Создает клавиатуру с кнопками для выбора карты
    :param cards: список номеров карт
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    for card in cards:
        button = InlineKeyboardButton(text=card, callback_data=f"card:{card}")
        keyboard.add(button)
    return keyboard