from typing import Optional

from ...models.rating_model import Rating
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['RatingRepository']


class RatingRepository(SqlAlchemyRepository[Rating]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Rating)

    async def put_rating(self, child_id: int, period_id: int, subject_id: int, number: int, avg: str, mood: str) -> Rating:
        return await self.create({
            'child_id': child_id,
            'period_id': period_id,
            'subject_id': subject_id,
            'number': number,
            'avg': avg,
            'mood': mood
        }, security=['child_id', 'period_id', 'subject_id'])

    async def get_rating(self, child_id: int, period_id: int, subject_id: int) -> Optional[Rating]:
        return await self.get_single(Rating.child_id == child_id, Rating.period_id == period_id, Rating.subject_id == subject_id)

    async def delete_rating(self, child_id: int, period_id: int, subject_id: int):
        await self.delete(Rating.child_id == child_id, Rating.period_id == period_id, Rating.subject_id == subject_id)
