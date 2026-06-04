from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_like_model import SchoolPostLike

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostLikeRepository']


class SchoolPostLikeRepository(SqlAlchemyRepository[SchoolPostLike]):
    """Репозиторий для работы с реакциями на посты"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPostLike)

    async def like_post(self, parent_id: int, post_id: int) -> SchoolPostLike:
        """
        Поставить реакцию на пост

        :param parent_id: идентификатор пользователя
        :param post_id: идентификатор поста
        :return: параметры реакции на пост
        """

        return await self.create({
            'parent_id': parent_id,
            'post_id': post_id
        })

    async def get_like(self, parent_id: int, post_id: int) -> Optional[SchoolPostLike]:
        """
        Получить реакцию пользователя на пост

        :param parent_id: идентификатор пользователя
        :param post_id: идентификатор поста
        :return: параметры реакции на пост, если существуют
        """

        return await self.get_single(
            SchoolPostLike.parent_id == parent_id, SchoolPostLike.post_id == post_id)

    async def has_my_likes(self, parent_id: int, posts_id: list[int]) -> list[SchoolPostLike]:
        """
        Получить реакции пользователя на посты

        :param parent_id: идентификатор пользователя
        :param posts_id: идентификаторы постов
        :return: список реакций на данные посты
        """

        return await self.get_multi(
            SchoolPostLike.parent_id == parent_id, SchoolPostLike.post_id.in_(posts_id))

    async def delete_like(self, parent_id: int, post_id: int):
        """
        Удалить реакцию на пост

        :param parent_id: идентификатор пользователя
        :param post_id: идентификатор поста
        """

        return await self.delete(SchoolPostLike.parent_id == parent_id, SchoolPostLike.post_id == post_id)
