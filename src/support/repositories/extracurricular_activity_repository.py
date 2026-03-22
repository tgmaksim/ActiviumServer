from ...repositories.db_queue import AsyncDBQueue
from ...models.extracurricular_activity_model import ExtracurricularActivity

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ExtracurricularActivityRepository']


class ExtracurricularActivityRepository(SqlAlchemyRepository[ExtracurricularActivity]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, ExtracurricularActivity)

    async def get_extracurricular_activities(self, school_id: int, group_id: int, days_hash: list[str]) -> list[ExtracurricularActivity]:
        return await self.get_multi(ExtracurricularActivity.school_id == school_id, ExtracurricularActivity.group_id == group_id, ExtracurricularActivity.day_hash.in_(days_hash))
