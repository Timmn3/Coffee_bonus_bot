from typing import List, Optional

from loguru import logger

from utils.db_api.shemas.polls import Polls


async def create_poll(question: str, options: List[str]) -> Optional[Polls]:
    """Создать новый опрос в базе данных."""

    try:
        poll = await Polls.create(
            question=question,
            options=options,
            votes=[0 for _ in options],
            is_active=True,
        )
        return poll
    except Exception as error:
        logger.exception(f'Ошибка при создании опроса: {error}')
        return None


async def update_poll_admin_message(poll_id: int, chat_id: int, message_id: int) -> bool:
    """Обновить информацию о сообщении администратора для опроса."""

    try:
        poll = await Polls.query.where(Polls.id == poll_id).gino.first()
        if not poll:
            logger.warning(f'Опрос с id={poll_id} не найден при обновлении admin_message_id.')
            return False

        await poll.update(admin_chat_id=chat_id, admin_message_id=message_id).apply()
        return True
    except Exception as error:
        logger.exception(f'Ошибка при обновлении сообщения администратора опроса: {error}')
        return False
