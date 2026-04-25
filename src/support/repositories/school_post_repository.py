from datetime import date
from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_model import SchoolPost

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostRepository']


class SchoolPostRepository(SqlAlchemyRepository[SchoolPost]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPost)

    async def get_school_posts(self, school_id: int, *, offset: int = 0, limit: int = 5) -> list[SchoolPost]:
        return await self.get_multi(SchoolPost.school_id == school_id, offset=offset, limit=limit)

    async def get_post(self, post_id: int) -> Optional[SchoolPost]:
        return await self.get_single(SchoolPost.post_id == post_id)

    async def create_post(self, school_id: int, timezone: int, *, title: str, description: Optional[str], has_image: bool, schedule_date: Optional[date], content: list[dict]) -> SchoolPost:
        return await self.create({
            'school_id': school_id,
            'timezone': timezone,
            'title': title,
            'description': description,
            'has_image': has_image,
            'schedule_date': schedule_date,
            'content': content
        })

    async def delete_post(self, post_id: int):
        return await self.delete(SchoolPost.post_id == post_id)
