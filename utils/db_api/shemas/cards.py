from data.config import TABLE_CARDS
from utils.db_api.db_gino import BaseModel, db

class Cards(BaseModel):
    __tablename__ = TABLE_CARDS

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'))
    card_number = db.Column(db.String(50))
    card_name = db.Column(db.String(100))
    bonus_account_id = db.Column(db.BigInteger, unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    active = db.Column(db.Boolean, default=True)
    bonus = db.Column(db.Float, default=0.0)