from sqlalchemy import JSON, BigInteger, Boolean, Column, Integer, Text

from app.db.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(Text)
    credits = Column(Integer, default=0, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    friends_invited = Column(Integer, nullable=True, default=0)
    limits = Column(JSON, nullable=True)
