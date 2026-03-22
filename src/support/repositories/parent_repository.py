from typing import Optional

from ...models.parent_model import Parent
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ParentRepository']


class ParentRepository(SqlAlchemyRepository[Parent]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Parent)

    async def get_parent(self, parent_id: int) -> Optional[Parent]:
        return await self.get_single(Parent.parent_id == parent_id)

    async def create_parent(self, parent_id: int, active_child_id: int) -> Parent:
        return await self.create({
            'parent_id': parent_id,
            'active_child_id': active_child_id
        })

    async def set_active_child(self, parent_id: int, active_child_id: int) -> Parent:
        return await self.update({
            'active_child_id': active_child_id
        }, Parent.parent_id == parent_id)
