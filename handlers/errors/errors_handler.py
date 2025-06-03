import logging

from aiogram.utils.exceptions import (Unauthorized, MessageCantBeDeleted, MessageToDeleteNotFound, MessageNotModified,
                                      MessageTextIsEmpty, CantParseEntities, CantDemoteChatCreator, InvalidQueryID,
                                      RetryAfter, TelegramAPIError, BadRequest)

from loader import dp

@dp.errors_handler()
async def errors_handler(update, exception):
    if isinstance(exception, Unauthorized):
        logging.info(f'Неавторизованный: {exception}')
        return True

    if isinstance(exception, MessageCantBeDeleted):
        logging.info('Сообщение не может быть удалено')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.info('Сообщение для удаления не найдено')
        return True

    if isinstance(exception, MessageNotModified):
        logging.info('Сообщение не изменено')
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logging.debug('Текст сообщения пуст')
        return True

    if isinstance(exception, CantParseEntities):
        logging.debug(f'Не удается разобрать объекты: {exception.args}')
        return True

    if isinstance(exception, CantDemoteChatCreator):
        logging.debug('Невозможно понизить создателя чата')
        return True

    if isinstance(exception, InvalidQueryID):
        logging.exception(f'Недопустимый идентификатор запроса: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, RetryAfter):
        logging.exception(f'Повторить после: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, BadRequest):
        logging.exception(f'Неверный запрос: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'Ошибка API Telegram: {exception} \nUpdate: {update}')
        return True

    # другая ошибка
    logging.exception(f'Другая ошибка: {exception} \nUpdate: {update}')
