import asyncio
import platform
from bs4 import BeautifulSoup
import requests

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# URL для страницы авторизации
login_url = 'https://p.vendista.ru/Auth/Login'


async def authorize(username, password):
    # Создаем сессию для обработки куков
    session = requests.Session()
    # Отправляем GET-запрос для получения страницы и извлечения токена
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    verification_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

    # URL и данные для аутентификации
    auth_url = 'https://p.vendista.ru/Auth/Login'
    login_data = {
        '__RequestVerificationToken': verification_token,
        'returnUrl': '',
        'Login': username,
        'Password': password,
    }

    # Отправляем POST-запрос для аутентификации
    session.post(auth_url, data=login_data)

    # URL для перехода после успешной авторизации
    bonuses_url = 'https://p.vendista.ru/Bonuses'

    # Отправляем GET-запрос для перехода по новому URL
    response_bonuses = session.get(bonuses_url)

    # Проверяем результат перехода
    try:
        # Извлекаем данные из таблицы
        soup_bonuses = BeautifulSoup(response_bonuses.text, 'html.parser').text
        print(soup_bonuses)
        return True

    except Exception:
        return False


async def main_authorize(username, password):
    result = await authorize(username, password)
    return result


# Запуск основной функции
if __name__ == '__main__':
    asyncio.run(main_authorize('golana127@mail.ru', 'qrjyat'))
