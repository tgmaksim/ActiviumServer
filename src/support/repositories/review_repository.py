from typing import Optional

from ...models.review_model import Review
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ReviewRepository']


class ReviewRepository(SqlAlchemyRepository[Review]):
    """Репозиторий для взаимодействия с отзывами пользователей"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Review)

    async def get_review(self, parent_id: int, only_is_open: bool = False) -> Optional[Review]:
        """
        Получить отзыв пользователя

        :param parent_id: идентификатор пользователя (владельца отзыва)
        :param only_is_open: только отзыв, прошедший модерацию
        :return: отзыв пользователя, если существует
        """

        return await self.get_single(
            Review.parent_id == parent_id,
            *((Review.is_open == True,) if only_is_open else ())
        )

    async def create_review(self, parent_id: int, name: str, stars: int, text: str, is_open: bool = False) -> Review:
        """
        Создать отзыв

        :param parent_id: идентификатор пользователя (владельца отзыва)
        :param name: имя пользователя, которое будет показано другим
        :param stars: оценка (число звезд) пользователя
        :param text: текст отзыва (необязательно)
        :param is_open: сразу опубликовать отзыв без модерации
        :return: созданный отзыв
        """

        return await self.create({
            'parent_id': parent_id,
            'name': name,
            'stars': stars,
            'text': text,
            'is_open': is_open
        })

    async def open_review(self, parent_id: int) -> Optional[Review]:
        """
        Опубликовать отзыв после модерации

        :param parent_id: идентификатор пользователя (владельца отзыва)
        :return: опубликованный отзыв, если существует
        """

        return await self.update({
            'is_open': True
        }, Review.parent_id == parent_id)

    async def update_review(
            self,
            parent_id: int,
            name: str,
            stars: int,
            text: Optional[str],
            is_updated: bool = True,
            is_open: bool = False
    ) -> Optional[Review]:
        """
        Отредактировать отзыв

        :param parent_id: идентификатор пользователя (владельца отзыва)
        :param name: имя пользователя, которое будет показано другим
        :param stars: оценка (число звезд) пользователя
        :param text: текст отзыва (необязательно)
        :param is_updated: пометить отзыв отредактированным
        :param is_open: сразу опубликовать отзыв без модерации
        :return: отредактированный отзыв, если существует
        """

        return await self.update({
            'name': name,
            'stars': stars,
            'text': text,
            'is_updated': is_updated,
            'is_open': is_open
        }, Review.parent_id == parent_id)

    async def delete_review(self, parent_id: int):
        """
        Удалить отзыв пользователя

        :param parent_id: идентификатор пользователя (владельца отзыва)
        """

        return await self.delete(Review.parent_id == parent_id)

    async def get_reviews_by_likes(self, offset: Optional[int], limit: int) -> list[Review]:
        """
        Получить отзывы, отсортированные по числу реакций

        :param offset: смещение списка
        :param limit: лимит запроса
        :return: список отзывов
        """

        return await self.get_multi(
            Review.is_open == True,
            orders_=(Review.likes.desc(), Review.created_at.desc()),
            offset=offset,
            limit=limit
        )

    async def get_reviews_by_max_stars(self, offset: Optional[int], limit: int) -> list[Review]:
        """
        Получить отзывы, отсортированные по оценке (от наибольших) и числу реакций

        :param offset: смещение списка
        :param limit: лимит запроса
        :return: список отзывов
        """

        return await self.get_multi(
            Review.is_open == True,
            orders_=(Review.stars.desc(), Review.likes.desc(), Review.created_at.desc()),
            offset=offset,
            limit=limit
        )

    async def get_reviews_by_min_stars(self, offset: Optional[int], limit: int) -> list[Review]:
        """
        Получить отзывы, отсортированные по оценке (от наименьших) и числу реакций

        :param offset: смещение списка
        :param limit: лимит запроса
        :return: список отзывов
        """

        return await self.get_multi(
            Review.is_open == True,
            orders_=(Review.stars, Review.likes.desc(), Review.created_at.desc()),
            offset=offset,
            limit=limit
        )

    async def like_review(self, parent_id: int) -> Optional[Review]:
        """
        Увеличить число отзывов у отзыва пользователя

        :param parent_id: идентификатор пользователя (владельца отзыва)
        :return: обновленный отзыв, если существует
        """

        return await self.update({
            'likes': Review.likes + 1
        }, Review.parent_id == parent_id)

    async def delete_like(self, parent_id: int) -> Optional[Review]:
        """
        Уменьшить число реакций у отзыва пользователя

        :param parent_id: идентификатор пользователя (владельца отзыва)
        :return: обновленный отзыв, если существует
        """

        return await self.update({
            'likes': Review.likes - 1
        }, Review.parent_id == parent_id)
