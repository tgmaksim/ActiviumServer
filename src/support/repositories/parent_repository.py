from typing import Optional

from ...models.parent_model import Parent
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ParentRepository']


class ParentRepository(SqlAlchemyRepository[Parent]):
    """Репозиторий для взаимодействия с пользователями"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Parent)

    async def get_parent(self, parent_id: int) -> Optional[Parent]:
        """
        Получения пользователя по идентификатору

        :param parent_id: идентификатор пользователя
        :return: пользователь, если существует
        """

        return await self.get_single(Parent.parent_id == parent_id)

    async def create_parent(self, parent_id: int) -> Parent:
        """
        Создание пользователя

        :param parent_id: идентификатор пользователя, взятый из Дневника.ру как person_id
        :return: новый пользователь
        """

        return await self.create({
            'parent_id': parent_id
        })

    async def get_parents(self, parents_id: list[int]) -> list[Parent]:
        """
        Получение пользователей по идентификаторам

        :param parents_id: идентификаторы пользователей
        :return: найденные пользователи
        """

        return await self.get_multi(Parent.parent_id.in_(parents_id))
