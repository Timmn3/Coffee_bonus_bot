import os

# Токен бота
BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
TABLE_NAME = str(os.getenv('TABLE_NAME'))
TABLE_CARDS = str(os.getenv('TABLE_CARDS'))
TABLE_POLLS = str(os.getenv('TABLE_POLLS', 'polls'))
ADMIN_IE = int(os.getenv('ADMIN_IE'))
USER_HELP = str(os.getenv('USER_HELP'))

# список администраторов бота
CODER = int(os.getenv('CODER'))

# ---------- База данных ----------
IP = os.getenv('IP', '127.0.0.1').strip()
PGUSER = str(os.getenv('PGUSER', 'postgres'))
PGPASSWORD = str(os.getenv('PGPASSWORD', ''))
DATABASE = str(os.getenv('DATABASE', 'postgres'))
PGPORT = str(os.getenv('PGPORT', '5432')).strip()

# Строка подключения с портом
POSTGRES_URI = f'postgresql://{PGUSER}:{PGPASSWORD}@{IP}:{PGPORT}/{DATABASE}'

# ---------- QIWI / Прочее ----------
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

# Telegram канал
CHANEL = os.getenv('CHANEL')

# Путь для логов
LOG_PATH = os.getenv('LOG_PATH')
