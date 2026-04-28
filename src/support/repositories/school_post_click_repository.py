from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_click_model import SchoolPostClick

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostClickRepository']


class SchoolPostClickRepository(SqlAlchemyRepository[SchoolPostClick]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPostClick)

    async def click_post(self, parent_id: int, post_id: int) -> SchoolPostClick:
        return await self.create({
            'parent_id': parent_id,
            'post_id': post_id
        })

    async def get_click(self, parent_id: int, post_id: int) -> Optional[SchoolPostClick]:
        return await self.get_single(
            SchoolPostClick.parent_id == parent_id, SchoolPostClick.post_id == post_id)

    async def has_my_clicks(self, parent_id: int, posts_id: list[int]) -> list[SchoolPostClick]:
        return await self.get_multi(
            SchoolPostClick.parent_id == parent_id, SchoolPostClick.post_id.in_(posts_id))
