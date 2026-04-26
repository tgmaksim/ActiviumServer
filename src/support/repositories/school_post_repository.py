from typing import Optional
from datetime import date, timedelta

from sqlalchemy import func, or_

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_model import SchoolPost

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostRepository']


class SchoolPostRepository(SqlAlchemyRepository[SchoolPost]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPost)

    async def get_admin_school_posts(self, school_id: int, *, offset: int = 0, limit: int = 5) -> list[SchoolPost]:
        return await self.get_multi(
            SchoolPost.school_id == school_id,
            orders_=SchoolPost.created_at.desc(),
            offset=offset, limit=limit
        )

    async def get_school_posts(self, school_id: int, *, last: Optional[timedelta] = None, offset: int = 0, limit: int = None) -> list[SchoolPost]:
        return await self.get_multi(
            or_(SchoolPost.school_id == school_id, SchoolPost.school_id == None),
            *((func.now() - SchoolPost.created_at <= last,) if last is not None else ()),
            orders_=SchoolPost.created_at.desc(),
            offset=offset, limit=limit
        )

    async def get_post(self, post_id: int) -> Optional[SchoolPost]:
        return await self.get_single(SchoolPost.post_id == post_id)

    async def create_post(self, school_id: int, timezone: int, *, title: str, description: Optional[str], has_image: bool, author: str, schedule_date: Optional[date], content: list[dict]) -> SchoolPost:
        return await self.create({
            'school_id': school_id,
            'timezone': timezone,
            'title': title,
            'description': description,
            'has_image': has_image,
            'author': author,
            'schedule_date': schedule_date,
            'content': content
        })

    async def delete_post(self, post_id: int):
        return await self.delete(SchoolPost.post_id == post_id)

    async def see_post(self, post_id: int) -> Optional[SchoolPost]:
        return await self.update({
            'count_visions': SchoolPost.count_visions + 1,
        }, SchoolPost.post_id == post_id)

    async def click_post(self, post_id: int) -> Optional[SchoolPost]:
        return await self.update({
            'count_clicks': SchoolPost.count_clicks + 1,
        }, SchoolPost.post_id == post_id)

    async def view_post(self, post_id: int) -> Optional[SchoolPost]:
        return await self.update({
            'count_viewings': SchoolPost.count_viewings + 1,
        }, SchoolPost.post_id == post_id)

    async def like_post(self, post_id: int) -> Optional[SchoolPost]:
        return await self.update({
            'count_likes': SchoolPost.count_likes + 1,
        }, SchoolPost.post_id == post_id)

    async def unlike_post(self, post_id: int) -> Optional[SchoolPost]:
        return await self.update({
            'count_likes': SchoolPost.count_likes - 1,
        }, SchoolPost.post_id == post_id)
