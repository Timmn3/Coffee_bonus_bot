from typing import List, Optional, Tuple
from loguru import logger
from utils.db_api.shemas.polls import Polls

async def create_poll(question: str, options: List[str], admin_chat_id: int) -> Optional[Polls]:
    """Создать новый опрос в базе данных с сохранением владельца (admin_chat_id)."""
    try:
        poll = await Polls.create(
            question=question,
            options=options,
            votes=[0 for _ in options],
            is_active=True,
            admin_chat_id=admin_chat_id,
            admin_message_id=None,  # больше не используем «админскую копию»
        )
        return poll
    except Exception as error:
        logger.exception(f'Ошибка при создании опроса: {error}')
        return None

# Оставляем функцию на будущее (не используется сейчас, но не мешает)
async def get_poll(poll_id: int) -> Optional[Polls]:
    """Получить опрос по id."""
    try:
        return await Polls.query.where(Polls.id == poll_id).gino.first()
    except Exception as error:
        logger.exception(f'Ошибка при получении опроса id={poll_id}: {error}')
        return None

async def increment_vote(poll_id: int, option_index: int) -> Optional[Polls]:
    """Инкремент счётчика голосов для варианта option_index."""
    try:
        poll = await get_poll(poll_id)
        if not poll or not poll.is_active:
            return poll
        votes = list(poll.votes or [])
        if 0 <= option_index < len(votes):
            votes[option_index] = int(votes[option_index]) + 1
            poll = await poll.update(votes=votes).apply()
        return poll
    except Exception as error:
        logger.exception(f'Ошибка при инкременте голоса poll_id={poll_id}: {error}')
        return None

def build_stats_text(question: str, options: List[str], votes: List[int]) -> Tuple[str, int]:
    """Сформировать текст статистики и вернуть (текст, total_votes)."""
    total = sum(int(v) for v in votes) if votes else 0
    lines = [f'<b>{question}</b>']
    for idx, opt in enumerate(options):
        v = int(votes[idx]) if idx < len(votes) else 0
        pct = (v * 100 / total) if total > 0 else 0.0
        lines.append(f'{idx + 1}. {opt} — <b>{v}</b> ({pct:.1f}%)')
    return '\n'.join(lines), total
