from typing import Optional

from ...models.hour_model import Hour
from ...models.hours_type import HoursType
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

    async def get_school_hour(self, school_id: int, hour_id: int) -> Optional[Hour]:
        """
        Получения конкретного звонкового распирания образовательной организации

        :param school_id: идентификатор образовательной организации
        :param hour_id: идентификатор звонкового расписания
        :return: конкретное звонковое расписание
        """

        return await self.get_single(Hour.school_id == school_id, Hour.hour_id == hour_id)

    async def delete_school_hour(self, school_id: int, hour_id: int):
        """
        Удаление звонкового расписания образовательной организации

        :param school_id: идентификатор образовательной организации
        :param hour_id: идентификатор звонкового расписания
        """

        return await self.delete(Hour.school_id == school_id, Hour.hour_id == hour_id)

    async def create_school_hour(self, school_id: int, months: list[int], weekdays: list[int], hours: list[HoursType]) -> Hour:
        """
        Добавление звонкового расписания образовательной организации

        :param school_id: идентификатор образовательной организации
        :param months: месяца звонкового расписания
        :param weekdays: дни недели звонкового расписания
        :param hours: новое звонковое расписание
        :return: новое звонковое расписание
        """

        return await self.create({
            'school_id': school_id,
            'months': months,
            'weekdays': weekdays,
            'hours': hours
        })

    async def update_school_hour(self, school_id: int, hour_id: int, months: list[int], weekdays: list[int], hours: list[HoursType]) -> Optional[Hour]:
        """
        Обновление или добавление звонкового расписания образовательной организации

        :param school_id: идентификатор образовательной организации
        :param hour_id: идентификатор звонкового расписания
        :param months: месяца звонкового расписания
        :param weekdays: дни недели звонкового расписания
        :param hours: новое звонковое расписание
        :return: измененное звонковое расписание, если существует
        """

        return await self.update(
            {
                'months': months,
                'weekdays': weekdays,
                'hours': hours
            },
            Hour.school_id == school_id, Hour.hour_id == hour_id
        )
