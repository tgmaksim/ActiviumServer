from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_vision_model import SchoolPostVision

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostVisionRepository']


class SchoolPostVisionRepository(SqlAlchemyRepository[SchoolPostVision]):
    """Репозиторий для работы с отметками "увидел" у постов"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPostVision)

    async def see_post(self, parent_id: int, post_id: int) -> SchoolPostVision:
        """
        Отметить пост увиденным

        :param parent_id: идентификатор пользователя
        :param post_id: идентификатор поста
        :return: параметры увиденного поста
        """

        return await self.create({
            'parent_id': parent_id,
            'post_id': post_id
        })

    async def get_vision(self, parent_id: int, post_id: int) -> Optional[SchoolPostVision]:
        """
        Получить отметку "увидел" пользователя у поста

        :param parent_id: идентификатор пользователя
        :param post_id: идентификатор поста
        :return: параметры увиденного поста, если существуют
        """

        return await self.get_single(
            SchoolPostVision.parent_id == parent_id, SchoolPostVision.post_id == post_id)

    async def has_my_visions(self, parent_id: int, posts_id: list[int]) -> list[SchoolPostVision]:
        """
        Получить отметки "увидел" пользователя на посты

        :param parent_id: идентификатор пользователя
        :param posts_id: идентификаторы постов
        :return: список отметок "увидел" на данные посты
        """

        return await self.get_multi(
            SchoolPostVision.parent_id == parent_id, SchoolPostVision.post_id.in_(posts_id))
