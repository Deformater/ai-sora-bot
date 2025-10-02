from uuid import uuid4

from sqlalchemy import UUID, DateTime, func
from sqlalchemy.orm import mapped_column

from app.db import DeclarativeBase


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id = mapped_column(
        UUID,
        primary_key=True,
        unique=True,
        doc="Unique id of the string in table",
        default=uuid4,
    )
    created_at = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        columns = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
