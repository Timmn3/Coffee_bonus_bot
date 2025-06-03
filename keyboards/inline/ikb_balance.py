from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ikb_balance = InlineKeyboardMarkup(row_width=1,
                                   inline_keyboard=[
                                       [
                                           InlineKeyboardButton(text="Пополнить", callback_data='Пополнить'),
                                       ]
                                   ])
# пополнить баланс
ikb_replenish_the_balance = InlineKeyboardMarkup(row_width=2,
                                                 inline_keyboard=[
                                                     [
                                                         InlineKeyboardButton(text="150 ₽", callback_data='150'),
                                                         InlineKeyboardButton(text="другая сумма",
                                                                              callback_data='другая сумма')
                                                     ]
                                                 ])

# проверить\отменить оплату
ikb_check_payment = InlineKeyboardMarkup(row_width=2,
                                         inline_keyboard=[
                                             [
                                                 InlineKeyboardButton(text="проверить", callback_data='проверить'),
                                                 InlineKeyboardButton(text="отменить", callback_data='отменить')
                                             ]
                                         ])
