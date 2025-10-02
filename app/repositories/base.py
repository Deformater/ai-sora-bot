from types import NoneType
from uuid import UUID

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyRepository:
    model = NoneType
    order_types = NoneType

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: UUID):
        query = select(cls.model).where(cls.model.id == id)  # type: ignore
        if hasattr(cls.model, "is_active"):
            query = query.where(cls.model.is_active)  # type: ignore
        result = await session.scalar(query)
        return result

    @classmethod
    async def add_one(cls, session: AsyncSession, data: dict, commit: bool = True):
        query = insert(cls.model).values(**data).returning(cls.model)
        result = await session.scalar(query)
        if commit:
            await session.commit()
        return result

    @classmethod
    async def update_by_id(cls, session: AsyncSession, id: UUID, data: dict):
        query = update(cls.model).where(cls.model.id == id).values(**data).returning(cls.model)  # type: ignore
        if hasattr(cls.model, "is_active"):
            query = query.where(cls.model.is_active)  # type: ignore
        result = await session.scalar(query)
        await session.commit()
        return result

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, id: UUID):
        query = delete(cls.model).where(cls.model.id == id).returning(cls.model)  # type: ignore
        if hasattr(cls.model, "is_active"):
            query = (
                update(cls.model)
                .where(cls.model.id == id)  # type: ignore
                .where(cls.model.is_active)  # type: ignore
                .values(is_active=False)
                .returning(cls.model)
            )
        result = await session.scalar(query)
        await session.commit()
        return result

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls.model)
        if hasattr(cls.model, "is_active"):
            query = query.where(cls.model.is_active)  # type: ignore
        if hasattr(cls.model, "order"):
            query = query.order_by(cls.model.order)  # type: ignore
        result = await session.scalars(query)
        return result
