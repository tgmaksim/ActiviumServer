from typing import Optional
from datetime import date, timedelta

from sqlalchemy import func, or_

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_model import SchoolPost, SchoolPostContentType

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostRepository']


class SchoolPostRepository(SqlAlchemyRepository[SchoolPost]):
    """Репозиторий для работы с постами образовательных организаций"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPost)

    async def get_admin_school_posts(self, school_id: int, *, offset: int = 0, limit: int = 5) -> list[SchoolPost]:
        """
        Получить посты для администратора образовательной организации

        :param school_id: идентификатор образовательной организации
        :param offset: смещение списка постов
        :param limit: лимит запроса
        """

        return await self.get_multi(
            SchoolPost.school_id == school_id,
            orders_=SchoolPost.created_at.desc(),
            offset=offset, limit=limit
        )

    async def get_school_posts(self, school_id: int, *, last: Optional[timedelta] = None, offset: int = 0, limit: int = None) -> list[SchoolPost]:
        """
        Получить посты для показа пользователю в ленте

        :param school_id: идентификатор образовательной организации, в которой состоит пользователь
        :param last: время, в течение которого доступны посты для просмотра
        :param offset: смещение списка постов
        :param limit: лимит запроса
        :return: список постов для показа
        """

        return await self.get_multi(
            or_(SchoolPost.school_id == school_id, SchoolPost.school_id == None),
            *((func.now() - SchoolPost.created_at <= last,) if last is not None else ()),
            orders_=SchoolPost.created_at.desc(),
            offset=offset, limit=limit
        )

    async def get_schedule_posts(self, school_id: int, start: date, end: date) -> list[SchoolPost]:
        """
        Получить посты с датами мероприятий

        :param school_id: идентификатор образовательной организации, в которой состоит пользователь
        :param start: начало периода
        :param end: конец периода
        :return: список постов с мероприятиями
        """

        return await self.get_multi(
            or_(SchoolPost.school_id == school_id, SchoolPost.school_id == None),
            SchoolPost.schedule_date != None,
            SchoolPost.schedule_date.between(start, end),
            orders_=SchoolPost.created_at.desc()
        )

    async def get_post(self, post_id: int) -> Optional[SchoolPost]:
        """
        Получить пост по идентификатору

        :param post_id: идентификатор поста
        :return: пост, если существует
        """

        return await self.get_single(SchoolPost.post_id == post_id)

    async def create_post(
            self,
            school_id: int,
            timezone: int,
            *,
            title: str,
            description: Optional[str],
            has_image: bool,
            author: str,
            schedule_date: Optional[date],
            content: list[SchoolPostContentType]
    ) -> SchoolPost:
        """
        Создать пост от образовательной организации

        :param school_id: идентификатор образовательной организации
        :param timezone: часовой пояс в секундах
        :param title: заголовок поста
        :param description: необязательное описание поста
        :param has_image: пост имеет главную фотографию
        :param author: имя автора поста
        :param schedule_date: дата мероприятия (необязательно)
        :param content: содержание поста формате JSONB
        """

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
        """
        Удалить пост

        :param post_id: идентификатор поста
        """

        return await self.delete(SchoolPost.post_id == post_id)

    async def see_post(self, post_id: int) -> Optional[SchoolPost]:
        """
        Увеличить число отметок "увидел" у поста

        :param post_id: идентификатор поста
        :return: обновленный пост
        """

        return await self.update({
            'count_visions': SchoolPost.count_visions + 1,
        }, SchoolPost.post_id == post_id)

    async def click_post(self, post_id: int) -> Optional[SchoolPost]:
        """
        Увеличить число открытий у поста

        :param post_id: идентификатор поста
        :return: обновленный пост
        """

        return await self.update({
            'count_clicks': SchoolPost.count_clicks + 1,
        }, SchoolPost.post_id == post_id)

    async def view_post(self, post_id: int) -> Optional[SchoolPost]:
        """
        Увеличить число просмотров у поста

        :param post_id: идентификатор поста
        :return: обновленный пост
        """

        return await self.update({
            'count_viewings': SchoolPost.count_viewings + 1,
        }, SchoolPost.post_id == post_id)

    async def like_post(self, post_id: int) -> Optional[SchoolPost]:
        """
        Увеличить число реакций у поста

        :param post_id: идентификатор поста
        :return: обновленный пост
        """

        return await self.update({
            'count_likes': SchoolPost.count_likes + 1,
        }, SchoolPost.post_id == post_id)

    async def unlike_post(self, post_id: int) -> Optional[SchoolPost]:
        """
        Уменьшить число реакций у поста

        :param post_id: идентификатор поста
        :return: обновленный пост
        """

        return await self.update({
            'count_likes': SchoolPost.count_likes - 1,
        }, SchoolPost.post_id == post_id)
