from typing import Optional

from ...models.child_model import Child
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ChildRepository']


class ChildRepository(SqlAlchemyRepository[Child]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Child)

    async def create_child(self, child_id: int, school_id: int, group_id: int, timezone: int, *, security: bool = False) -> Child:
        return await self.create({
            'child_id': child_id,
            'school_id': school_id,
            'group_id': group_id,
            'timezone': timezone
        }, security=['child_id'] if security else None)

    async def get_child(self, child_id: int) -> Optional[Child]:
        return await self.get_single(Child.child_id == child_id)

    async def update_child(
            self,
            child_id: int,
            *,
            school_id: int = None,
            group_id: int = None,
            timezone: int = None
    ) -> Optional[Child]:
        update = {}
        if school_id is not None:
            update['school_id'] = school_id
        if group_id is not None:
            update['group_id'] = group_id
        if timezone is not None:
            update['timezone'] = timezone

        return await self.update(update, Child.child_id == child_id)
