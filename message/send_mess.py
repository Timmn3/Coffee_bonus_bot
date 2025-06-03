from loader import dp
from asyncio import sleep


async def send_mess_users(text, users_id):
    if isinstance(users_id, int):
        users_id = [users_id]  # Преобразование в список
    for user_id in users_id:
        if user_id is not None:
            await dp.bot.send_message(chat_id=user_id, text=text)
            await sleep(0.25)  # 4 сообщения в секунду
