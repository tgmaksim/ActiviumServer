from typing import Optional

from ...models.hour_model import Hour
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['HourRepository']


class HourRepository(SqlAlchemyRepository[Hour]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Hour)

    async def get_hours(self, school_id: int, month: int, weekday: int) -> Optional[Hour]:
        return await self.get_single(Hour.school_id == school_id, Hour.months.contains([month]), Hour.weekdays.contains([weekday]))
