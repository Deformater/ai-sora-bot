from sqlalchemy import BigInteger, Column, Integer, Text, JSON

from app.db.models.base import BaseModel


class Price(BaseModel):
    __tablename__ = "prices"

    name = Column(Text, nullable=False)
    plan_id = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    currency = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)
    credits = Column(Integer, default=0, nullable=True)
    price = Column(Integer, default=0, nullable=False)
    limits = Column(JSON, nullable=True)
