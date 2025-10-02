from contextlib import contextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import get_settings


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()
        self.refresh_sync()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance  # noqa

    def refresh(self) -> None:
        settings = get_settings()
        self.engine = create_async_engine(
            settings.database_uri,
            future=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=0,
            pool_pre_ping=True,
        )
        self.session_maker = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore

    def refresh_sync(self) -> None:
        settings = get_settings()
        sync_engine = create_engine(
            settings.database_uri_sync,
            pool_size=settings.DB_POOL_SIZE,
            echo=False,
        )
        self.session_maker_sync = sessionmaker(sync_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_manager = SessionManager()
    async with session_manager.session_maker() as session:  # type: ignore
        yield session


@contextmanager
def get_session_sync():
    session_manager = SessionManager()
    with session_manager.session_maker_sync() as session:  # type: ignore
        yield session
