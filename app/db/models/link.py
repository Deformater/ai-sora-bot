from sqlalchemy import Column, Integer, Text

from app.db.models.base import BaseModel


class Link(BaseModel):
    __tablename__ = "links"

    name = Column(Text, nullable=False, unique=True)
    counter = Column(Integer, nullable=False, default=0)
    link = Column(Text, nullable=False)
