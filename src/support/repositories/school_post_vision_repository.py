from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_vision_model import SchoolPostVision

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostVisionRepository']


class SchoolPostVisionRepository(SqlAlchemyRepository[SchoolPostVision]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPostVision)

    async def see_post(self, parent_id: int, post_id: int) -> SchoolPostVision:
        return await self.create({
            'parent_id': parent_id,
            'post_id': post_id
        })

    async def get_vision(self, parent_id: int, post_id: int) -> Optional[SchoolPostVision]:
        return await self.get_single(SchoolPostVision.parent_id == parent_id, SchoolPostVision.post_id == post_id)

    async def has_my_visions(self, parent_id: int, posts_id: list[int]) -> list[SchoolPostVision]:
        return await self.get_multi(SchoolPostVision.parent_id == parent_id, SchoolPostVision.post_id.in_(posts_id))
