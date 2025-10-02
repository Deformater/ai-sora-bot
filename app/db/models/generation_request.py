from sqlalchemy import BigInteger, Column, Enum, ForeignKey, Integer, Text, JSON

from app.db.models.base import BaseModel
from app.utils.enum import GenerationRequestStatus


class GenerationRequest(BaseModel):
    __tablename__ = "generation_requests"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    api = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    cost = Column(Integer, nullable=False)
    request_params = Column(JSON, nullable=False)
    result_urls = Column(JSON, nullable=True)
    task_id = Column(Text, nullable=True)
    status = Column(
        Enum(GenerationRequestStatus),
        default=GenerationRequestStatus.PENDING,
    )
    msg = Column(Text, nullable=True)
