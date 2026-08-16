from datetime import datetime
from typing import Optional

from sqlalchemy import select, distinct

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

    async def get_groups(self, school_id: int, since: datetime, offset: int, limit: int) -> list[int]:
        """
        Получение идентификаторов учебных групп (классов) у внеурочных занятий в образовательной организации от нужной даты

        :param school_id: идентификатор образовательной организации
        :param since: начальная дата сбора внеурочных занятий
        :param offset: смещение списка
        :param limit: лимит запроса
        :return: идентификаторы учебных групп (классов)
        """

        statement = (
            select(distinct(ExtracurricularActivity.group_id))
            .where(ExtracurricularActivity.school_id == school_id)
            .where(ExtracurricularActivity.start_time >= since)
            .offset(offset)
            .limit(limit)
        )

        res = await self.queue.execute(statement)
        return res.scalars().all()

    async def get_subject_place_by_group(
            self,
            school_id: int,
            group_id: int,
            since: datetime,
            offset: int,
            limit: int
    ) -> list[tuple[str, str]]:
        """
        Получение предметов и мест проведения внеурочных занятий
        в учебной группе (классе) образовательной организации от нужной даты

        :param school_id: идентификатор образовательной организации
        :param group_id: идентификатор учебной группы (класса)
        :param since: начальная дата сбора внеурочных занятий
        :param offset: смещение списка
        :param limit: лимит запроса
        :return: список внеурочных занятий
        """

        statement = (
            select(ExtracurricularActivity.subject, ExtracurricularActivity.place)
            .distinct(ExtracurricularActivity.subject, ExtracurricularActivity.place)
            .where(ExtracurricularActivity.school_id == school_id)
            .where(ExtracurricularActivity.group_id == group_id)
            .where(ExtracurricularActivity.start_time >= since)
            .offset(offset)
            .limit(limit)
        )

        res = await self.queue.execute(statement)
        return res.all()

    async def get_extracurricular_activities_by_subject_place(
            self,
            school_id: int,
            group_id: int,
            subject: str,
            place: str,
            since: datetime,
            offset: int,
            limit: int
    ) -> list[ExtracurricularActivity]:
        """
        Получение внеурочных занятий в учебной группе (классе) образовательной организации по предмету в кабинете

        :param school_id: идентификатор образовательной организации
        :param group_id: идентификатор учебной группы (класса)
        :param subject: название предмета
        :param place: место проведения (кабинет)
        :param since: начальная дата сбора внеурочных занятий
        :param offset: смещение списка
        :param limit: лимит запроса
        :return: список внеурочных занятий
        """

        return await self.get_multi(
            ExtracurricularActivity.school_id == school_id,
            ExtracurricularActivity.group_id == group_id,
            ExtracurricularActivity.subject == subject,
            ExtracurricularActivity.place == place,
            ExtracurricularActivity.start_time >= since,
            offset=offset, limit=limit
        )

    async def get_extracurricular_activity(self, school_id: int, ea_id: int) -> Optional[ExtracurricularActivity]:
        """
        Получение внеурочного занятия в образовательной организации

        :param school_id: идентификатор образовательной организации
        :param ea_id: идентификатор внеурочного занятия
        :return: внеурочное занятие, если существует
        """

        return await self.get_single(
            ExtracurricularActivity.ea_id == ea_id,
            ExtracurricularActivity.school_id == school_id
        )

    async def delete_all_school(self, school_id: int):
        """
        Удаление всех внеурочных занятий в образовательной организации

        :param school_id: идентификатор образовательной организации
        """

        return await self.delete(ExtracurricularActivity.school_id == school_id)

    async def delete_extracurricular_activities_by_subject_place(self, school_id: int, group_id: int, subject: str, place: str):
        """
        Удаление внеурочных занятий в учебной группе (классе) образовательной организации по предмету в кабинете

        :param school_id: идентификатор образовательной организации
        :param group_id: идентификатор учебной группы (класса)
        :param subject: название предмета
        :param place: место проведения
        """

        return await self.delete(
            ExtracurricularActivity.school_id == school_id,
            ExtracurricularActivity.group_id == group_id,
            ExtracurricularActivity.subject == subject,
            ExtracurricularActivity.place == place
        )

    async def delete_extracurricular_activity(self, school_id: int, ea_id: int):
        """
        Удаление конкретного внеурочного занятия в образовательной организации

        :param school_id: идентификатор образовательной организации
        :param ea_id: идентификатор внеурочного занятия
        """

        return await self.delete(ExtracurricularActivity.ea_id == ea_id, ExtracurricularActivity.school_id == school_id)
