from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_viewing_model import SchoolPostViewing

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostViewingRepository']


class SchoolPostViewingRepository(SqlAlchemyRepository[SchoolPostViewing]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPostViewing)

    async def view_post(self, parent_id: int, post_id: int) -> SchoolPostViewing:
        return await self.create({
            'parent_id': parent_id,
            'post_id': post_id
        })

    async def get_view(self, parent_id: int, post_id: int) -> Optional[SchoolPostViewing]:
        return await self.get_single(SchoolPostViewing.parent_id == parent_id, SchoolPostViewing.post_id == post_id)

    async def has_my_viewings(self, parent_id: int, posts_id: list[int]) -> list[SchoolPostViewing]:
        return await self.get_multi(SchoolPostViewing.parent_id == parent_id, SchoolPostViewing.post_id.in_(posts_id))
