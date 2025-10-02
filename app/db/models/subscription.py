from __future__ import annotations

from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, BigInteger, Text

from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

from app.db.models.base import BaseModel
from app.db.models.transaction import Transaction


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    transaction_id = Column(UUID, ForeignKey("transactions.id"), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    payment_method_id = Column(Text, nullable=False)

    transaction: Mapped["Transaction"] = relationship(back_populates="subscription")
