from typing import Callable, Self

from sqlalchemy.ext.asyncio import AsyncSession

from .base_uow import UnitOfWork
from .db_queue import AsyncDBQueue


__all__ = ['SqlAlchemyUnitOfWork']


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self.queue = AsyncDBQueue(self.session)
        await self.queue.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_val:
                await self.queue.rollback()
            else:
                await self.queue.commit()
        finally:
            await self.queue.stop()
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
