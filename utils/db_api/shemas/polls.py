from sqlalchemy import BigInteger, Boolean, Column, Integer, JSON, String

from data.config import TABLE_POLLS
from utils.db_api.db_gino import TimedBaseModel


class Polls(TimedBaseModel):
    __tablename__ = TABLE_POLLS

    id = Column(Integer, primary_key=True)
    question = Column(String(500), nullable=False)
    options = Column(JSON, nullable=False)
    votes = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    admin_chat_id = Column(BigInteger, nullable=True)
    admin_message_id = Column(BigInteger, nullable=True)
