from aiogram import types
from aiogram.utils.deep_linking import get_start_link
from loader import dp
from utils.db_api.users_commands import get_bonus


@dp.message_handler(text="/my_bonuses")
async def my_bonuses(message: types.Message):
    bonus = await get_bonus(message.from_user.id)
    if bonus:
        await message.answer(f'У Вас {bonus} бонусов✅\n'
                             f'<b>1 бонус = 1 рублю!</b>\n'
                             f'Вы можете выбрать напиток и приложить карту как обычно к терминалу!\n'
                             f'При достаточном наличии бонусов деньги не списываются и у Вас будет написано '
                             f'<b>"бесплатная продажа"!</b>')
    else:
        await message.answer(f'Совершите оплату в кофеаппарате, что бы появились бонусы!')
