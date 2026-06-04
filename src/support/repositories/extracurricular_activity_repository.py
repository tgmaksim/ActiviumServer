from datetime import datetime

from ...repositories.db_queue import AsyncDBQueue
from ...models.extracurricular_activity_model import ExtracurricularActivity

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ExtracurricularActivityRepository']


class ExtracurricularActivityRepository(SqlAlchemyRepository[ExtracurricularActivity]):
    """Репозиторий для работы с внеурочными занятиями в расписании"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, ExtracurricularActivity)

    async def get_extracurricular_activities(
            self,
            school_id: int,
            group_id: int,
            period: tuple[datetime, datetime]
    ) -> list[ExtracurricularActivity]:
        """
        Получение внеурочных занятий учебной группы (класса) в образовательной организации в течение периода

        :param school_id: идентификатор образовательной организации
        :param group_id: идентификатор учебной группы (класса), в которой проводятся внеурочные занятия
        :param period: период, в котором необходимо найти внеурочные занятия
        :return: список внеурочных занятий учебной группы (класса) в образовательной организации в течение периода
        """

        return await self.get_multi(
            ExtracurricularActivity.school_id == school_id,
            ExtracurricularActivity.group_id == group_id,
            ExtracurricularActivity.start_time.between(*period),
            orders_=ExtracurricularActivity.start_time.asc()
        )
