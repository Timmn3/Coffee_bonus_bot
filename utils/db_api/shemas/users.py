from sqlalchemy import Column, BigInteger, String, sql, Float, Boolean, JSON

from data.config import TABLE_NAME
from utils.db_api.db_gino import TimedBaseModel


class Users(TimedBaseModel):
    __tablename__ = TABLE_NAME
    user_id = Column(BigInteger, primary_key=True)
    tg_first_name = Column(String(250))
    tg_last_name = Column(String(250))
    name = Column(String(100))
    card_number = Column(String(50))
    name_cards = Column(JSON, default={})
    phone_number = Column(String(50))
    status = Column(String(25))
    bonus = Column(JSON)
    number_ie = Column(BigInteger)
    sms_status = Column(Boolean)
    bonus_account_id = Column(BigInteger, unique=True, nullable=True)

    query: sql.select
