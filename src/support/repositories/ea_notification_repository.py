from typing import Optional

from sqlalchemy import select, tuple_

from ...models.child_model import Child
from ...repositories.db_queue import AsyncDBQueue
from ...models.ea_notification_model import EANotification

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['EANotificationRepository']


class EANotificationRepository(SqlAlchemyRepository[EANotification]):
    """Репозиторий для работы функции уведомлений с напоминанием о внеурочных занятиях"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, EANotification)

    async def get_status(self, session_id: str, child_id: int) -> Optional[EANotification]:
        """
        Получение статуса функции уведомлений с напоминанием о внеурочных занятиях для ребенка (профиля) у сессии.
        Функция работает независимо на разных сессиях и для разных детей (профилей)

        :param session_id: идентификатор сессии, у которой проверяется статус функции
        :param child_id: идентификатор ребенка (профиля), для которой проверяется статус функции
        :return: параметры включенной функции или None, если она выключена
        """

        return await self.get_single(
            EANotification.session_id == session_id, EANotification.child_id == child_id)

    async def turn_off(self, session_id: str, child_id: int):
        """
        Выключение функции уведомлений с напоминанием о внеурочных занятиях для ребенка (профиля) у сессии

        :param session_id: идентификатор сессии, у которой выключается функция
        :param child_id: идентификатор ребенка (профиля), для которой выключается функция
        """

        return await self.delete(EANotification.session_id == session_id, EANotification.child_id == child_id)

    async def turn_on(self, session_id: str, child_id: int) -> EANotification:
        """
        Включение функции уведомлений с напоминанием о внеурочных занятиях для ребенка (профиля) у сессии

        :param session_id: идентификатор сессии, у которой включается функция
        :param child_id: идентификатор ребенка (профиля), для которой включается функция
        :return: параметры включенной функции
        """

        return await self.create({
            'session_id': session_id,
            'child_id': child_id
        }, security=['session_id', 'child_id'], security_nothing=True)

    async def get_notifications(self, groups: list[tuple[int, int]]) -> list[EANotification]:
        """
        Получение списка с параметрами включенных функций у каждой сессии для каждого ребенка (профиля),
        который состоит в одной из учебных групп (классах) образовательных организаций

        :param groups: список пар (идентификатор образовательной организации, идентификатор учебной группы (класса))
        :return: список с параметрами включенных функций
        """

        # Проверка каждой записи, что ребенок (профиль), который привязан, состоит в одной из учебных групп (классов)
        statement = (
            select(EANotification)
            .join(EANotification.child)
            .where(
                tuple_(Child.school_id, Child.group_id).in_(groups)
            )
        )

        res = await self.queue.execute(statement)
        return res.scalars().all()
