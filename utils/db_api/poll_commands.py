from typing import List, Optional, Tuple

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


# ==== Новые функции для работы с голосами и статистикой ==== #

async def get_poll(poll_id: int) -> Optional[Polls]:
    """Получить опрос по id."""
    try:
        return await Polls.query.where(Polls.id == poll_id).gino.first()
    except Exception as error:
        logger.exception(f'Ошибка при получении опроса id={poll_id}: {error}')
        return None


async def increment_vote(poll_id: int, option_index: int) -> Optional[Polls]:
    """
    Увеличить счётчик голосов для варианта option_index.
    Возвращает обновлённый объект опроса или None в случае ошибки.
    """
    try:
        poll = await get_poll(poll_id)
        if not poll:
            logger.warning(f'Опрос id={poll_id} не найден для increment_vote.')
            return None
        if not poll.is_active:
            logger.info(f'Опрос id={poll_id} неактивен — голос не учитывается.')
            return poll

        votes = list(poll.votes or [])
        if option_index < 0 or option_index >= len(votes):
            logger.warning(f'Неверный индекс варианта: {option_index} для poll_id={poll_id}')
            return poll

        votes[option_index] = int(votes[option_index]) + 1
        poll = await poll.update(votes=votes).apply()
        return poll
    except Exception as error:
        logger.exception(f'Ошибка при инкременте голоса poll_id={poll_id}: {error}')
        return None


def build_stats_text(question: str, options: List[str], votes: List[int]) -> Tuple[str, int]:
    """
    Сформировать текст статистики.
    Возвращает (текст, total_votes).
    """
    total = sum(int(v) for v in votes) if votes else 0
    lines = [f'<b>{question}</b>']
    for idx, opt in enumerate(options):
        v = int(votes[idx]) if idx < len(votes) else 0
        pct = (v * 100 / total) if total > 0 else 0.0
        lines.append(f'{idx + 1}. {opt} — <b>{v}</b> ({pct:.1f}%)')
    return '\n'.join(lines), total
