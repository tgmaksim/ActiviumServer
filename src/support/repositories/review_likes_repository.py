from typing import Optional

from sqlalchemy import select

from ...repositories.db_queue import AsyncDBQueue
from ...models.review_like_model import ReviewLike

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ReviewLikeRepository']


class ReviewLikeRepository(SqlAlchemyRepository[ReviewLike]):
    """Репозиторий для взаимодействия с реакциями на отзывы пользователей"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, ReviewLike)

    async def like_review(self, parent_id: int, review_id: int) -> ReviewLike:
        """
        Поставить реакцию на отзыв пользователя

        :param parent_id: идентификатор пользователя, который ставить реакцию
        :param review_id: идентификатор отзыва (владельца отзыва)
        :return: параметры реакции на отзыв пользователя
        """

        return await self.create({
            'parent_id': parent_id,
            'review_id': review_id
        })

    async def get_like(self, parent_id: int, review_id: int) -> Optional[ReviewLike]:
        """
        Получить параметры реакции на отзыв пользователя

        :param parent_id: идентификатор пользователя, который поставил реакцию
        :param review_id: идентификатор отзыва (владельца отзыва)
        :return: параметры реакции на отзыв пользователя, если реакция есть
        """

        return await self.get_single(ReviewLike.parent_id == parent_id, ReviewLike.review_id == review_id)

    async def has_my_likes(self, parent_id: int, reviews_id: list[int]) -> set[int]:
        """
        Получение реакций на данные отзывы пользователей

        :param parent_id: идентификатор пользователя, который поставил реакции
        :param reviews_id: идентификаторы отзывов (владельцев отзывов), среди которых проводится проверка
        :return: идентификаторы отзывов, на которых поставлена реакция пользователем
        """

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
        """
        Удалить реакцию на отзыв пользователя

        :param parent_id: идентификатор пользователя, который поставил реакцию
        :param review_id: идентификатор отзыва (владельца отзыва)
        """

        return await self.delete(ReviewLike.parent_id == parent_id, ReviewLike.review_id == review_id)
