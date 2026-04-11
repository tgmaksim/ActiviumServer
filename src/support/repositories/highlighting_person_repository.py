from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.highlighting_person_model import HighlightingPerson

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['HighlightingPersonRepository']


class HighlightingPersonRepository(SqlAlchemyRepository[HighlightingPerson]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, HighlightingPerson)

    async def get_highlighting_person(self, parent_id: int, person_id: int) -> Optional[HighlightingPerson]:
        return await self.get_single(HighlightingPerson.parent_id == parent_id, HighlightingPerson.person_id == person_id)

    async def get_highlighting_persons(self, parent_id: int) -> list[HighlightingPerson]:
        return await self.get_multi(HighlightingPerson.parent_id == parent_id)

    async def highlight_person(self, parent_id: int, person_id: int):
        await self.create({
            'parent_id': parent_id,
            'person_id': person_id
        }, security=['parent_id', 'person_id'], security_nothing=True)

    async def unhighlight_person(self, parent_id: int, person_id: int):
        return await self.delete(HighlightingPerson.parent_id == parent_id, HighlightingPerson.person_id == person_id)