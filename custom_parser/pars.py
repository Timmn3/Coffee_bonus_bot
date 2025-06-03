import requests
import asyncio
from bs4 import BeautifulSoup
from loguru import logger

from data.config import CODER
from filters.admins import Admins
from utils.db_api.ie_commands import change_last_time, get_last_time
from datetime import datetime
from loader import bot
from fake_useragent import UserAgent

from utils.db_api.users_commands import get_user_id_by_card_number, update_bonus


async def current_time_formatted():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d.%m.%Y %H:%M:%S")
    return formatted_time


async def compare_dates(date_str_pars, date_str_bd):
    # Преобразование строк в объекты datetime
    date_str_pars = datetime.strptime(date_str_pars, '%d.%m.%Y %H:%M:%S')
    date_str_bd = datetime.strptime(date_str_bd, '%d.%m.%Y %H:%M:%S')

    # Сравнение дат
    if date_str_pars > date_str_bd:
        return True
    else:
        return False


async def parse_amount_string(amount_str):
    try:
        # Удаляем два последних символа и заменяем запятую на точку
        amount_str_cleaned = amount_str.replace("\xa0", "").replace(" ", "")[:-2].replace(",", ".")
        # Преобразуем строку в тип float
        amount_float = float(amount_str_cleaned)
        return amount_float
    except ValueError:
        # Если возникла ошибка при преобразовании, например, из-за неправильного формата строки
        return None


stop_flag = False  # Глобальная переменная для управления циклом


class AsyncLoginSessionManager:
    instance = None  # Статическое поле для хранения экземпляра

    def __init__(self, login_url='https://p.vendista.ru/Auth/Login'):
        self.login_url = login_url
        self.session = None  # Инициализировать сеанс как Нет
        self.user_agent = UserAgent()

    async def __aenter__(self):
        self.session = requests.Session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.session.close()

    async def login(self, login, password):
        response = self.session.get(self.login_url)
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        verification_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

        auth_url = 'https://p.vendista.ru/Auth/Login'
        login_data = {
            '__RequestVerificationToken': verification_token,
            'returnUrl': '',
            'Login': login,
            'Password': password,
        }

        response = self.session.post(auth_url, data=login_data, headers={'User-Agent': self.user_agent.random})
        if response.ok:
            return True
        else:
            logger.error('Authentication failed!')
            await bot.send_message(chat_id=CODER, text=f'Authentication failed! /run')
            return False

    async def get_bonuses_data(self, user_data):
        user_id = user_data['user_id']
        try:
            while not stop_flag:  # Проверяйте флаг перед каждой итерацией
                unique_card_numbers = set()
                for page_number in range(1, 2):
                    bonuses_url_page = f'https://p.vendista.ru/Bonuses?OrderByColumn=3&OrderDesc=True&PageNumber={page_number}&ItemsOnPage=200&FilterText='

                    response_bonuses = self.session.get(bonuses_url_page, headers={'User-Agent': self.user_agent.random})
                    html_bonuses_page = response_bonuses.text
                    # текущее время
                    date_str_now = str(await current_time_formatted())
                    soup_bonuses_page = BeautifulSoup(html_bonuses_page, 'html.parser')
                    rows = soup_bonuses_page.select('.catalog__body .row')

                    # время из БД последнего запроса
                    date_str_bd = await get_last_time(int(user_id))
                    date_str_bd = '02.06.2025 06:00:00'
                    counter = 0
                    for row in rows:
                        if counter >= 50:
                            break
                        columns = row.select('.catalog__table_td')
                        if columns:
                            card_number = columns[1].text.strip()
                            bonus_balance = columns[3].text.strip()
                            sale_time = columns[4].text.strip()
                            unique_card_numbers.add(card_number)
                            counter += 1
                            # сравниваем время последнего обновления со временем последней покупки
                            if await compare_dates(sale_time, date_str_bd):

                                # смотрим у какого пользователя совпадает номер карты
                                user = await get_user_id_by_card_number(card_number)
                                if user:
                                    bonuses = f'бонусы 💳{card_number}: {bonus_balance}'
                                    # отправляем сообщение пользователю
                                    # await bot.send_message(user, bonuses)
                                    print(user, bonuses)
                                    # отправляем админу
                                    # await bot.send_message(chat_id=CODER, text=f'{user}\n{sale_time}\n{bonuses}')
                                    # сохраняем количество бонусов в БД
                                    bonus = await parse_amount_string(bonus_balance)
                                    await update_bonus(user, bonus)
                    # сохраняем текущее время в БД
                    await change_last_time(user_id, date_str_now)
                await asyncio.sleep(30)
        except Exception as e:
            logger.error(f'Ошибка извлечения бонусных данных!', e)
            await asyncio.sleep(60)
            date_str_now = str(await current_time_formatted())
            # сохраняем текущее время в БД
            await change_last_time(user_id, date_str_now)
            await bot.send_message(chat_id=CODER, text=f'Ошибка извлечения бонусных данных /run!')

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance


async def stop_processing():
    global stop_flag
    stop_flag = True  # Установите флаг, чтобы остановить обработку


async def start_processing():
    global stop_flag
    stop_flag = False  # Установите флаг, чтобы начать обработку


async def process_user(user_data):
    async with AsyncLoginSessionManager() as async_session_manager:
        try:
            if await async_session_manager.login(user_data['login'], user_data['password']):
                await async_session_manager.get_bonuses_data(user_data)
        except asyncio.CancelledError:
            pass  # При необходимости обработайте исключение отмены.

        await stop_processing()  # Остановить обработку после выполнения задачи


async def parsing_main(users_data):
    tasks = [process_user(user_data) for user_data in users_data]
    await asyncio.gather(*tasks)
