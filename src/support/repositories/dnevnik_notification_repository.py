from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, update

from ...repositories.db_queue import AsyncDBQueue
from ...models.dnevnik_notification_model import DnevnikNotification

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['DnevnikNotificationRepository']


class DnevnikNotificationRepository(SqlAlchemyRepository[DnevnikNotification]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, DnevnikNotification)

    async def get_status(self, session_id: str, child_id: int) -> Optional[DnevnikNotification]:
        return await self.get_single(DnevnikNotification.session_id == session_id, DnevnikNotification.child_id == child_id)

    async def turn_off(self, session_id: str, child_id: int):
        await self.delete(DnevnikNotification.session_id == session_id, DnevnikNotification.child_id == child_id)

    async def turn_on(self, session_id: str, child_id: int) -> DnevnikNotification:
        return await self.create({
            'session_id': session_id,
            'child_id': child_id
        })

    async def get_count(self) -> int:
        statement = select(func.count(DnevnikNotification.child_id))
        res = await self.queue.execute(statement)
        return res.scalar() or 0

    async def get_next_child(self) -> list[DnevnikNotification]:
        subquery = (
            select(DnevnikNotification.child_id)
            .group_by(DnevnikNotification.child_id)
            .order_by(func.min(DnevnikNotification.updated_at))
            .limit(1)
            .cte('next_child')
        )
        statement = select(DnevnikNotification).join(subquery, DnevnikNotification.child_id == subquery.c.child_id).with_for_update(skip_locked=True)
        res = await self.queue.execute(statement)

        return res.scalars().all()

    async def update_date(self, child_id: int, last_mark: Optional[datetime]):
        statement = (
            update(DnevnikNotification)
            .where(DnevnikNotification.child_id == child_id)
            .values(last_mark=last_mark or DnevnikNotification.last_mark)
        )
        await self.queue.execute(statement)
