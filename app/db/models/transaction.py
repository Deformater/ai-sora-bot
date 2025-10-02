from sqlalchemy import Column, ForeignKey, BigInteger, Text, UUID

from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

from app.db.models.base import BaseModel
from app.db.models.price import Price


class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    price_id = Column(UUID, ForeignKey("prices.id"), nullable=False)
    status = Column(Text, nullable=True)
    payment_id = Column(Text, nullable=True)

    price: Mapped["Price"] = relationship(backref="transactions")
    subscription: Mapped["Subscription"] = relationship(back_populates="transaction")
