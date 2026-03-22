from typing import Optional

from sqlalchemy import select

from ...models.likes_review import ReviewLike
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ReviewLikeRepository']


class ReviewLikeRepository(SqlAlchemyRepository[ReviewLike]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, ReviewLike)

    async def like_review(self, parent_id: int, review_id: int) -> ReviewLike:
        return await self.create({
            'parent_id': parent_id,
            'review_id': review_id
        })

    async def get_like(self, parent_id: int, review_id: int) -> Optional[ReviewLike]:
        return await self.get_single(ReviewLike.parent_id == parent_id, ReviewLike.review_id == review_id)

    async def has_my_likes(self, parent_id: int, reviews_id: list[int]) -> set[int]:
        statement = (
            select(ReviewLike.review_id)
            .where(
                ReviewLike.parent_id == parent_id,
                ReviewLike.review_id.in_(reviews_id)
            )
        )

        res = await self.queue.execute(statement)
        return set(res.scalars().all())

    async def delete_like(self, parent_id: int, review_id: int):
        return await self.delete(ReviewLike.parent_id == parent_id, ReviewLike.review_id == review_id)
