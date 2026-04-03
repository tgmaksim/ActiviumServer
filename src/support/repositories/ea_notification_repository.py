from typing import Optional

from sqlalchemy import select, tuple_

from ...models.child_model import Child
from ...repositories.db_queue import AsyncDBQueue
from ...models.ea_notification_model import EANotification

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['EANotificationRepository']


class EANotificationRepository(SqlAlchemyRepository[EANotification]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, EANotification)

    async def get_status(self, session_id: str, child_id: int) -> Optional[EANotification]:
        return await self.get_single(EANotification.session_id == session_id, EANotification.child_id == child_id)

    async def turn_off(self, session_id: str, child_id: int):
        await self.delete(EANotification.session_id == session_id, EANotification.child_id == child_id)

    async def turn_on(self, session_id: str, child_id: int) -> EANotification:
        return await self.create({
            'session_id': session_id,
            'child_id': child_id
        })

    async def get_notifications(self, groups: list[tuple[int, int]]) -> list[EANotification]:
        statement = (
            select(EANotification)
            .join(EANotification.child)
            .where(
                tuple_(Child.school_id, Child.group_id).in_(groups)
            )
        )

        res = await self.queue.execute(statement)
        return res.scalars().all()
