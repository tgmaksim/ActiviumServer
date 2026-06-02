from typing import Optional

from ...models.child_model import Child
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ChildRepository']


class ChildRepository(SqlAlchemyRepository[Child]):
    """Репозиторий для взаимодействия с детьми (профилями) пользователей"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Child)

    async def create_child(
            self,
            child_id: int,
            school_id: int,
            group_id: int,
            timezone: int,
            *,
            security: bool = False
    ) -> Child:
        """
        Создание ребенка (профиля) пользователя

        :param child_id: идентификатор ребенка (профиля), взятый из Дневника.ру как person_id
        :param school_id: идентификатор образовательной организации ребенка (профиля) из Дневника.ру
        :param group_id: идентификатор учебной группы (класса) из Дневника.ру
        :param timezone: часовой пояс в секундах ребенка (профиля)
        :param security: обновить данные ребенка, если такой уже добавлен
        :return: ребенок (профиль)
        """

        return await self.create({
            'child_id': child_id,
            'school_id': school_id,
            'group_id': group_id,
            'timezone': timezone
        }, security=['child_id'] if security else None)

    async def get_child(self, child_id: int) -> Optional[Child]:
        """
        Получение ребенка (профиля) по его идентификатору

        :param child_id: идентификатор ребенка (профиля), взятый из Дневника.ру как person_id
        :return: ребенок (профиль), если такой существует
        """

        return await self.get_single(Child.child_id == child_id)

    async def update_child(
            self,
            child_id: int,
            *,
            school_id: int = None,
            group_id: int = None,
            timezone: int = None
    ) -> Optional[Child]:
        """
        Обновление данных ребенка (профиля). При отсутствии какого-либо параметра он не изменяется

        :param child_id: идентификатор ребенка (профиля)
        :param school_id: идентификатор образовательной организации ребенка (профиля)
        :param group_id: идентификатор учебной группы (класса) ребенка (профиля)
        :param timezone: часовой пояс в секундах ребенка (профиля)
        :return: ребенок (профиль), если такой существует
        """

        update = {}
        if school_id is not None:
            update['school_id'] = school_id
        if group_id is not None:
            update['group_id'] = group_id
        if timezone is not None:
            update['timezone'] = timezone

        return await self.update(update, Child.child_id == child_id)
