from sqlalchemy import Column, BigInteger, String, sql, Float, Boolean

from utils.db_api.db_gino import TimedBaseModel


class IndividualEntrepreneur(TimedBaseModel):
    __tablename__ = 'Individual_entrepreneur'
    user_id = Column(BigInteger, primary_key=True)
    tg_first_name = Column(String(250))
    tg_last_name = Column(String(250))
    name = Column(String(100))
    email = Column(String(50))
    password = Column(String(50))
    time_update = Column(BigInteger)
    last_time = Column(String(100))
    status = Column(String(25))
    is_run = Column(Boolean)
    balance = Column(Float)
    number_ie = Column(BigInteger)
    sms_status = Column(Boolean)
    bill_id = Column(String(200))
    report_time = Column(String(100))
    report_state = Column(Boolean)
    bot_name = Column(String(100))
    token = Column(String(100))

    query: sql.select
