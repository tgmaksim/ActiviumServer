from typing import Optional

from ...models.hour_model import Hour
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['HourRepository']


class HourRepository(SqlAlchemyRepository[Hour]):
    """Репозиторий для работы со звонковым расписанием, отличным от Дневника.ру"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Hour)

    async def get_school_hours(self, school_id: int) -> list[Hour]:
        """
        Получение звонковых расписаний образовательной организации

        :param school_id: идентификатор образовательной организации
        :return: список звонковых расписаний в зависимости от месяца и дня недели
        """

        return await self.get_multi(Hour.school_id == school_id)
