import os

from dotenv import load_dotenv

# запускаем функцию, которая загружает переменное окружение из файла .env
load_dotenv()

# Токен бота
BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
TABLE_NAME = str(os.getenv('TABLE_NAME'))
ADMIN_IE = int(os.getenv('ADMIN_IE'))
USER_HELP = str(os.getenv('USER_HELP'))

# список администраторов бота
CODER = os.getenv('CODER')

ip = os.getenv('IP')
PGUSER = str(os.getenv('PGUSER'))
PGPASSWORD = str(os.getenv('PGPASSWORD'))
DATABASE = str(os.getenv('DATABASE'))

POSTGRES_URI = f'postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}'

QIWI_TOKEN = os.getenv('QIWI')
WALLET_QIWI = os.getenv('WALLET')
QIWI_PUB_KEY = os.getenv('QIWI_PUB_KEY')
QIWI_PRIV_KEY = os.getenv('QIWI_PRIV_KEY')


# Время напоминания
REMINDER_DAY = os.getenv('REMINDER_DAY', '2')
REMINDER_HOUR = os.getenv('REMINDER_HOUR', '12')
REMINDER_MINUTE = os.getenv('REMINDER_MINUTE', '0')

# Флаг необходимости уведомления
SEND_PAYMENT_REMINDER = os.getenv('SEND_PAYMENT_REMINDER', 'True').lower() in ('true', '1', 'yes')

# Номер карты для абонплаты
PAYMENT_CARD = os.getenv('PAYMENT_CARD')