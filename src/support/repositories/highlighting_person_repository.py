from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.highlighting_person_model import HighlightingPerson

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['HighlightingPersonRepository']


class HighlightingPersonRepository(SqlAlchemyRepository[HighlightingPerson]):
    """Репозиторий для взаимодействия с выделенными одноклассниками в рейтингах"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, HighlightingPerson)

    async def get_highlighting_person(self, parent_id: int, person_id: int) -> Optional[HighlightingPerson]:
        """
        Получение выделенного одноклассника в рейтингах, если он выделен

        :param parent_id: идентификатор пользователя, для которого одноклассник выделен
        :param person_id: идентификатор выделенного одноклассника в рейтингах, взятый из Дневника.ру
        :return: параметры выделенного одноклассника в рейтингах, если он выделен
        """

        return await self.get_single(
            HighlightingPerson.parent_id == parent_id, HighlightingPerson.person_id == person_id)

    async def get_highlighting_persons(self, parent_id: int) -> list[HighlightingPerson]:
        """
        Получение всех выделенных одноклассников в рейтингах у пользователя

        :param parent_id: идентификатор пользователя
        :return: список всех выделенных одноклассников в рейтингах у пользователя
        """

        return await self.get_multi(HighlightingPerson.parent_id == parent_id)

    async def highlight_person(self, parent_id: int, person_id: int) -> HighlightingPerson:
        """
        Выделить одноклассника в рейтингах для пользователя

        :param parent_id: идентификатор пользователя
        :param person_id: идентификатор одноклассника, взятый из Дневника.ру
        :return: параметры выделенного одноклассника в рейтингах
        """

        return await self.create({
            'parent_id': parent_id,
            'person_id': person_id
        }, security=['parent_id', 'person_id'], security_nothing=True)

    async def unhighlight_person(self, parent_id: int, person_id: int):
        """
        Снять выделение с одноклассника в рейтингах у пользователя

        :param parent_id: идентификатор пользователя
        :param person_id: идентификатор одноклассника, с которого снять выделение
        """

        return await self.delete(
            HighlightingPerson.parent_id == parent_id, HighlightingPerson.person_id == person_id)