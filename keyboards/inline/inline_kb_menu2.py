from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ikb_menu2 = InlineKeyboardMarkup(row_width=2,
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(text="Сообщение", callback_data='Сообщение'),
                                        InlineKeyboardButton(text="Ссылка", url='https://www.youtube.com/watch?v=DUhE01MPMwM&ab_channel=%D0%9D%D0%B5%D0%BC%D0%BD%D0%BE%D0%B3%D0%BE%D0%9B%D1%83%D1%87%D1%88%D0%B5'),
                                    ],
                                ])