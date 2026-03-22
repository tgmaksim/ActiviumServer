from contextlib import asynccontextmanager

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .db_config import settings_db


__all__ = ['db_helper']


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo, pool_pre_ping=True)

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession
        )

    @asynccontextmanager
    async def get_db_session(self):
        async with self.session_factory() as session:
            try:
                yield session
            except exc.SQLAlchemyError:
                await session.rollback()
                raise

    async def dispose(self):
        await self.engine.dispose()


db_helper = DatabaseHelper(settings_db.database_url, settings_db.DB_ECHO)
