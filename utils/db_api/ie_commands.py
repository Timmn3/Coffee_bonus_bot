from asyncpg import UniqueViolationError
from loguru import logger

from utils.db_api.db_gino import db
from utils.db_api.shemas.ie import IndividualEntrepreneur


async def add_ie(user_id: int, tg_first_name: str, tg_last_name: str, name: str, email: str, password: str,
                 time_update: int, last_time: str, status: str, is_run: bool, balance: float, number_ie: int,
                 sms_status: bool, bill_id: str, report_time: str, report_state: bool, bot_name: str, token: str):
    try:
        ie = IndividualEntrepreneur(user_id=user_id, tg_first_name=tg_first_name, tg_last_name=tg_last_name,
                                    name=name, email=email, password=password, time_update=time_update,
                                    last_time=last_time, status=status, is_run=is_run, balance=balance,
                                    number_ie=number_ie, sms_status=sms_status, bill_id=bill_id,
                                    report_time=report_time, report_state=report_state, bot_name=bot_name, token=token)
        await ie.create()
    except UniqueViolationError:
        logger.exception('Ошибка при добавлении ИП')


async def count_users():
    try:
        count = await db.func.count(IndividualEntrepreneur.user_id).gino.scalar()
        return count
    except Exception as e:
        logger.exception(f'Ошибка при подсчете пользователей: {e}')
        return None


async def select_user(user_id):
    try:
        user = await IndividualEntrepreneur.query.where(IndividualEntrepreneur.user_id == user_id).gino.first()
        return user
    except Exception as e:
        logger.exception(f'Ошибка при выборе пользователя: {e}')


async def db_run_stop(user_id: int, value: bool):
    """ функция внесения в БД состояния работы парсинга"""
    try:
        user = await select_user(user_id)
        await user.update(is_run=value).apply()
    except Exception as e:
        logger.exception(f'Ошибка при изменении is_run пользователя: {e}')


async def reset_all_users_is_run():
    """ Устанавливаем всем пользователям False"""
    try:
        await IndividualEntrepreneur.update.values(is_run=False).gino.status()
    except Exception as e:
        logger.exception(f'Ошибка при сбросе поля is_run для всех пользователей: {e}')


async def is_running(user_id: int):
    """ Проверка состояния запущенного парсинга"""
    try:
        user = await select_user(user_id)
        if user:
            return user.is_run
        else:
            return None
    except Exception as e:
        logger.exception(f'Ошибка при получении состояния is_run пользователя: {e}')


async def get_user_data_email_password_time(user_id):
    try:
        user = await select_user(user_id)
        if user:
            return {
                'email': user.email,
                'password': user.password,
                'time_update': user.time_update,
            }
        else:
            return None
    except Exception as e:
        logger.exception(f'Ошибка при получении данных пользователя: {e}')


async def change_user_email(user_id: int, new_email: str):
    try:
        user = await select_user(user_id)
        await user.update(email=new_email).apply()
    except Exception as e:
        logger.exception(f'Ошибка при изменении email пользователя: {e}')


async def get_user_email(user_id: int):
    try:
        user = await select_user(user_id)
        if user is not None:
            return user.email
        else:
            return None
    except Exception as e:
        logger.exception(f'Ошибка при запросе email пользователя: {e}')


async def get_user_password(user_id: int):
    try:
        user = await IndividualEntrepreneur.query.where(IndividualEntrepreneur.user_id == user_id).gino.first()
        if user:
            return user.password
        else:
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка получения пароля для пользователя {user_id}: {e}')
        return None  # or raise an exception if you prefer


async def get_users_data_all():
    try:
        users_data = []
        users = await IndividualEntrepreneur.query.where(IndividualEntrepreneur.is_run == True).gino.all()

        for user in users:
            user_data = {
                'user_id': user.user_id,
                'login': user.email,
                'password': user.password,
            }
            users_data.append(user_data)

        return users_data
    except Exception as e:
        logger.exception(f'Ошибка при получении данных пользователей: {e}')
        return None


async def get_user_data(user_id):
    try:
        user = await IndividualEntrepreneur.query.where(
            (IndividualEntrepreneur.user_id == user_id) &
            (IndividualEntrepreneur.is_run == True)
        ).gino.first()

        if user:
            user_data = {
                'user_id': user.user_id,
                'login': user.email,
                'password': user.password,
            }
            return [user_data]
        else:
            logger.warning(f'Пользователь с user_id {user_id} не найден или неактивен.')
            return None
    except Exception as e:
        logger.exception(f'Ошибка при получении данных пользователя с user_id {user_id}: {e}')
        return None


async def count_ie():
    try:
        count = await db.func.count(IndividualEntrepreneur.user_id).gino.scalar()
        return count
    except Exception as e:
        logger.exception(f'Ошибка при подсчете пользователей: {e}')
        return None


async def change_user_password(user_id: int, new_password: str):
    try:
        user = await select_user(user_id)
        await user.update(password=new_password).apply()
    except Exception as e:
        logger.exception(f'Ошибка при изменении пароля пользователя: {e}')


async def update_status(user_id, status):
    try:
        user = await select_user(user_id)
        await user.update(status=status).apply()
    except Exception as e:
        logger.exception(f'Ошибка при обновлении статуса пользователя: {e}')


async def check_args(args, user_id: int):
    try:
        if args == '':
            args = '0'
            return args
        elif not args.isnumeric():
            args = '0'
            return args
        elif args.isnumeric():
            if int(args) == user_id:
                args = '0'
                return args
            elif await select_user(user_id=int(args)) is None:
                args = '0'
                return args
            else:
                args = str(args)
                return args
        else:
            args = '0'
            return args
    except Exception as e:
        logger.exception(f'Ошибка при проверке аргументов: {e}')


async def change_balance(user_id: int, amount):
    try:
        user = await select_user(user_id)
        new_balance = float(user.balance) + float(amount)
        await user.update(balance=new_balance).apply()
    except Exception as e:
        logger.exception(f'Ошибка при изменении баланса пользователя: {e}')


async def check_balance(user_id: int, amount):
    try:
        user = await select_user(user_id=user_id)
        try:
            amount = float(amount)
            if user.balance + amount >= 0:
                await change_balance(user_id, amount)
                return True
            elif user.balance + amount < 0:
                return 'no maney'
        except Exception as e:
            logger.exception(e)
            return False
    except Exception as e:
        logger.exception(f'Ошибка при проверке баланса: {e}')


async def user_balance(user_id: int):  # какой баланс у пользователя
    user = await select_user(user_id)  # получаем юзера
    try:
        return user.balance
    except Exception as e:
        logger.exception(f'Ошибка user_balance: {e}')
        return False


async def user_bill_id(user_id: int):  # получаем идентификатор заказа
    user = await select_user(user_id)  # получаем юзера
    return user.bill_id


async def change_bill_id(user_id: int, value):  # изменяем идентификатор заказа
    user = await select_user(user_id)
    new_bill_id = value
    await user.update(bill_id=new_bill_id).apply()


async def clear_bill_id(user_id: int):  # очищаем идентификатор заказа
    user = await select_user(user_id)
    await user.update(bill_id='').apply()


# выбрать всех пользователей с необходимым балансом
async def select_all_users_big_balance():
    users = await IndividualEntrepreneur.select('user_id').where(IndividualEntrepreneur.balance > 4).gino.all()
    return users


# выбрать всех пользователей с балансом меньше 15 рублей
async def select_all_users_balance_lower():
    users = await IndividualEntrepreneur.select('user_id').where(IndividualEntrepreneur.balance < 15).gino.all()
    return users


async def change_email_and_password(user_id: int, new_email: str, new_password: str):
    """ Измените адрес электронной почты и пароль"""
    try:
        user = await select_user(user_id)
        await user.update(email=new_email, password=new_password).apply()
    except Exception as e:
        logger.exception(f'Ошибка при изменении email и пароля пользователя: {e}')


async def get_sms_status_ie(user_id: int):
    """ Получить статус SMS предпринимателя """
    try:
        # Выбираем пользователя
        user = await IndividualEntrepreneur.query.where(IndividualEntrepreneur.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем статус SMS
            return user.sms_status
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить статус SMS.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении статуса SMS пользователя: {e}')
        return None  # or raise an exception if you prefer


async def update_sms_status(user_id: int, new_sms_status: bool):
    """ Обновить СМС-статус для ИП."""
    try:
        user = await select_user(user_id)
        if user:
            await user.update(sms_status=new_sms_status).apply()
        else:
            logger.warning(f"User with ID {user_id} not found. Cannot update SMS status.")
    except Exception as e:
        logger.exception(f'Error updating SMS status for user {user_id}: {e}')


async def get_report_time(user_id: int):
    """ Получение report_time для пользователя"""
    try:
        user = await IndividualEntrepreneur.query.where(IndividualEntrepreneur.user_id == user_id).gino.first()
        if user:
            return user.report_time
        else:
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка получения report_time для пользователя {user_id}: {e}')
        return None  # or raise an exception if you prefer


async def get_report_state(user_id: int):
    try:
        user = await IndividualEntrepreneur.query.where(IndividualEntrepreneur.user_id == user_id).gino.first()
        if user:
            return user.report_state
        else:
            return None  # или создайте исключение, если хотите
    except Exception as e:
        logger.exception(f'Ошибка получения report_state для пользователя {user_id}: {e}')
        return None  # или создайте исключение, если хотите


async def update_report_state(user_id: int, new_report_state: bool):
    """ Обновление report_state для ИП."""
    try:
        user = await select_user(user_id)
        if user:
            await user.update(report_state=new_report_state).apply()
        else:
            logger.warning(f"Пользователь с идентификатором {user_id} не найден. Невозможно обновить report_state.")
    except Exception as e:
        logger.exception(f'Ошибка обновления report_state для пользователя. {user_id}: {e}')


async def update_report_time(user_id: int, new_report_time: str):
    """ Обновление report_time для ИП."""
    try:
        user = await select_user(user_id)
        if user:
            await user.update(report_time=new_report_time).apply()
        else:
            logger.warning(f"Пользователь с идентификатором {user_id} не найден. Невозможно обновить report_time.")
    except Exception as e:
        logger.exception(f'Ошибка обновления report_time для пользователя {user_id}: {e}')


async def change_last_time(user_id: int, last_time_new: str):
    try:
        user = await select_user(user_id)
        await user.update(last_time=last_time_new).apply()
    except Exception as e:
        logger.exception(f'Ошибка при изменении last_time пользователя: {e}')


async def get_last_time(user_id: int):
    try:
        user = await select_user(user_id)
        if user:
            return user.last_time
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить last_time.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении last_time пользователя: {e}')
        return None  # or raise an exception if you prefer
