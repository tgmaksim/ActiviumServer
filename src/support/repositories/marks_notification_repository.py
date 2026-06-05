from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, distinct

from ...repositories.db_queue import AsyncDBQueue
from ...models.marks_notification_model import MarksNotification

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['MarksNotificationRepository']


class MarksNotificationRepository(SqlAlchemyRepository[MarksNotification]):
    """Репозиторий для работы функции уведомлений о новых оценках"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, MarksNotification)

    async def get_status(self, session_id: str, child_id: int) -> Optional[MarksNotification]:
        """
        Получение статуса функции уведомлений о новых оценках для ребенка (профиля) у сессии.
        Функция работает независимо на разных сессиях и для разных детей (профилей)

        :param session_id: идентификатор сессии, у которой проверяется статус функции
        :param child_id: идентификатор ребенка (профиля), для которой проверяется статус функции
        :return: параметры включенной функции или None, если она выключена
        """

        return await self.get_single(
            MarksNotification.session_id == session_id, MarksNotification.child_id == child_id)

    async def turn_off(self, session_id: str, child_id: int):
        """
        Выключение функции уведомлений о новых оценках для ребенка (профиля) у сессии

        :param session_id: идентификатор сессии, у которой выключается функция
        :param child_id: идентификатор ребенка (профиля), для которой выключается функция
        """

        return await self.delete(MarksNotification.session_id == session_id, MarksNotification.child_id == child_id)

    async def turn_on(self, session_id: str, child_id: int) -> MarksNotification:
        """
        Включение функции уведомлений о новых оценках для ребенка (профиля) у сессии

        :param session_id: идентификатор сессии, у которой включается функция
        :param child_id: идентификатор ребенка (профиля), для которой включается функция
        :return: параметры включенной функции
        """

        return await self.create({
            'session_id': session_id,
            'child_id': child_id
        }, security=['session_id', 'child_id'], security_nothing=True)

    async def get_count(self) -> int:
        """
        Получение числа детей (профилей), у которых включена функция уведомлений о новых оценках

        :return: число уникальных child_id
        """

        statement = select(func.count(distinct(MarksNotification.child_id)))
        res = await self.queue.execute(statement)
        return res.scalar() or 0

    async def get_next_child(self) -> list[MarksNotification]:
        """
        Получение следующих сессий, у которых включена функция уведомлений о новых оценках, с одним ребенком (профилем).
        Используется skip_locked для правильной конкурентной работы нескольких worker'ов

        :return: список параметров функции для сессий с одним ребенком (профилем)
        """

        # Получение идентификатора ребенка (профиля), который проверялся позднее всех
        subquery = (
            select(MarksNotification.child_id)
            .group_by(MarksNotification.child_id)
            .order_by(func.min(MarksNotification.updated_at))
            .limit(1)
            .cte('next_child')
        )

        # Получение всех сессий, у которых включена функция, с этим ребенком (профилем)
        statement = (
            select(MarksNotification)
            .join(subquery, MarksNotification.child_id == subquery.c.child_id)
            .with_for_update(skip_locked=True)
        )

        res = await self.queue.execute(statement)
        return res.scalars().all()

    async def update_date(self, child_id: int, last_mark: Optional[datetime]) -> list[MarksNotification]:
        """
        Обновление времени последней обработки ребенка (профиля) у всех сессий для проверки новых оценок

        :param child_id: идентификатор ребенка (профиля)
        :param last_mark: время выставления последней оценки, если выставлена новая
        :return: обновленные параметры функции всех сессий
        """

        # Если last_mark = None, то обновится только created_at
        return await self.update_many({
            'last_mark': last_mark or MarksNotification.last_mark
        }, MarksNotification.child_id == child_id)
