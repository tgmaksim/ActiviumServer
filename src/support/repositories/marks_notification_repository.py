from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, update

from ...repositories.db_queue import AsyncDBQueue
from ...models.marks_notification_model import MarksNotification

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['MarksNotificationRepository']


class MarksNotificationRepository(SqlAlchemyRepository[MarksNotification]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, MarksNotification)

    async def get_status(self, session_id: str, child_id: int) -> Optional[MarksNotification]:
        return await self.get_single(MarksNotification.session_id == session_id, MarksNotification.child_id == child_id)

    async def turn_off(self, session_id: str, child_id: int):
        await self.delete(MarksNotification.session_id == session_id, MarksNotification.child_id == child_id)

    async def turn_on(self, session_id: str, child_id: int) -> MarksNotification:
        return await self.create({
            'session_id': session_id,
            'child_id': child_id
        })

    async def get_count(self) -> int:
        statement = select(func.count(MarksNotification.child_id))
        res = await self.queue.execute(statement)
        return res.scalar() or 0

    async def get_next_child(self) -> list[MarksNotification]:
        subquery = (
            select(MarksNotification.child_id)
            .group_by(MarksNotification.child_id)
            .order_by(func.min(MarksNotification.updated_at))
            .limit(1)
            .cte('next_child')
        )
        statement = select(MarksNotification).join(subquery, MarksNotification.child_id == subquery.c.child_id).with_for_update(skip_locked=True)

        res = await self.queue.execute(statement)
        return res.scalars().all()

    async def update_date(self, child_id: int, last_mark: Optional[datetime]):
        statement = (
            update(MarksNotification)
            .where(MarksNotification.child_id == child_id)
            .values(last_mark=last_mark or MarksNotification.last_mark)
        )
        await self.queue.execute(statement)
