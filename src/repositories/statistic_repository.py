from typing import Optional
from datetime import datetime

from sqlalchemy import select, func

from .db_queue import AsyncDBQueue
from .sqlalchemy_repository import SqlAlchemyRepository

from ..models.statistic_model import Statistic


__all__ = ['StatisticRepository']


class StatisticRepository(SqlAlchemyRepository[Statistic]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Statistic)

    async def add_statistic(self, parent_id: Optional[int], key: str):
        await self.create({
            "parent_id": parent_id,
            "key": key
        })

    async def get_count_unique_users(self, since: datetime) -> int:
        statement = select(func.count(func.distinct(Statistic.parent_id))).where(Statistic.created_at > since)

        res = await self.queue.execute(statement)
        return res.scalar_one()

    async def get_group_statistics(self, since: datetime) -> list[tuple[str, int]]:
        """[(key, count), ...]"""

        statement = select(Statistic.key, func.count().label('count')).where(Statistic.created_at > since).group_by(Statistic.key)

        res = await self.queue.execute(statement)
        return res.all()
