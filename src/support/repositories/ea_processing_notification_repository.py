from datetime import datetime

from sqlalchemy import select, func

from ...repositories.db_queue import AsyncDBQueue
from ...models.ea_processing_notification_model import EAProcessingNotification

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['EAProcessingNotificationRepository']


class EAProcessingNotificationRepository(SqlAlchemyRepository[EAProcessingNotification]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, EAProcessingNotification)

    async def get_next_extracurricular_activities(self, start_time_period: tuple[datetime, datetime]) -> list[EAProcessingNotification]:
        subquery = (
            select(EAProcessingNotification.start_time)
            .where(EAProcessingNotification.start_time.between(*start_time_period))
            .group_by(EAProcessingNotification.start_time)
            .order_by(EAProcessingNotification.start_time)
            .limit(1)
            .cte('next_time')
        )

        statement = (
            select(EAProcessingNotification)
            .join(subquery, EAProcessingNotification.start_time == subquery.c.start_time)
            .with_for_update(skip_locked=True)
        )

        res = await self.queue.execute(statement)
        return res.scalars().all()

    async def finish_process(self, ea_id: int):
        return await self.delete(EAProcessingNotification.ea_id == ea_id)

    async def delete_overdue_ea(self):
        return await self.delete(EAProcessingNotification.start_time < func.now())
