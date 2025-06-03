from sqlalchemy import Column, BigInteger, String, sql, Float, Boolean

from data.config import TABLE_NAME
from utils.db_api.db_gino import TimedBaseModel


class Users(TimedBaseModel):
    __tablename__ = TABLE_NAME
    user_id = Column(BigInteger, primary_key=True)
    tg_first_name = Column(String(250))
    tg_last_name = Column(String(250))
    name = Column(String(100))
    card_number = Column(String(50))
    phone_number = Column(String(50))
    status = Column(String(25))
    bonus = Column(Float)
    number_ie = Column(BigInteger)
    sms_status = Column(Boolean)

    query: sql.select
