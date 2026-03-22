from typing import Optional
from datetime import timedelta, datetime

from sqlalchemy import select, func

from .db_queue import AsyncDBQueue
from ..models.monitorig_model import Monitoring
from .sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['MonitoringRepository']


class MonitoringRepository(SqlAlchemyRepository[Monitoring]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Monitoring)

    async def add_monitoring(
            self,
            *,
            path: str,
            session_id: Optional[str] = None,
            status: bool = True,
            duration: timedelta,
    ):
        await self.create({
            'path': path,
            'session_id': session_id,
            'status': status,
            'duration': duration
        })

    async def get_stats(self, since: datetime) -> list[tuple[str, timedelta, timedelta, timedelta]]:
        """[(path, min_duration, max_duration, media_duration), ...]"""

        statement = (
            select(
                Monitoring.path,
                func.min(Monitoring.duration).label("min_duration"),
                func.max(Monitoring.duration).label("max_duration"),
                func.percentile_cont(0.5)
                .within_group(Monitoring.duration)
                .label("median_duration"),
            )
            .where(Monitoring.status.is_(True), Monitoring.created_at > since)
            .group_by(Monitoring.path)
        )

        res = await self.queue.execute(statement)
        return [row.tuple() for row in res.all()]
