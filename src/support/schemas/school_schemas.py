import datetime

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse

from pydantic import Field
from typing import ClassVar, Literal, Optional


__all__ = ['SchoolPost', 'SchoolPostsResult', 'SchoolPostsApiResponse', 'SchoolPostsWithoutVisionResult',
           'SchoolPostsWithoutVisionApiResponse', 'SeeSchoolPostApiResponse', 'ClickSchoolPostApiResponse',
           'ViewSchoolPostResult', 'ViewSchoolPostApiResponse', 'LikeSchoolPostResult', 'LikeSchoolPostApiResponse',
           'UnlikeSchoolPostResult', 'UnlikeSchoolPostApiResponse']


class SchoolPost(ApiBase):
    """Школьный пост"""

    classId: ClassVar[int] = 0x4E
    class_id: Literal[0x4E] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    postId: int = Field(
        description="Идентификатор поста"
    )
    title: str = Field(
        description="Заголовок поста"
    )
    description: Optional[str] = Field(
        description="Короткое описание поста, если есть"
    )
    imageUrl: Optional[str] = Field(
        description="Ссылка на главную картинку поста"
    )
    author: str = Field(
        description="Имя автора поста"
    )
    authorVerified: bool = Field(
        description="Автор является сотрудником Активиум"
    )
    scheduleDate: Optional[datetime.date] = Field(
        description="Дата мероприятия в расписании"
    )
    isUpdated: bool = Field(
        description="Пост был отредактирован после написания"
    )
    countViewings: int = Field(
        description="Количество полных просмотров поста"
    )
    countLikes: int = Field(
        description="Количество реакций"
    )
    hasMyLike: bool = Field(
        description="Поставлена реакция на пост"
    )
    postUrl: str = Field(
        description="Ссылка на открытие поста"
    )


class SchoolPostsResult(ApiBase):
    """Результат запроса получения последних постов"""

    classId: ClassVar[int] = 0x4F
    class_id: Literal[0x4F] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    posts: list[SchoolPost] = Field(
        description="Список постов"
    )
    nextOffset: Optional[int] = Field(
        description="Смещение для получения следующих постов"
    )


class SchoolPostsApiResponse(ApiResponse):
    """Ответ на запрос получения последних постов"""

    classId: ClassVar[int] = 0x50
    class_id: Literal[0x50, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[SchoolPostsResult] = Field(
        default=None,
        description="Список последних постов"
    )


class SchoolPostsWithoutVisionResult(ApiBase):
    """Результат запроса получения неувиденных постов"""

    classId: ClassVar[int] = 0x51
    class_id: Literal[0x51] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    countPosts: int = Field(
        description="Количество неувиденных постов"
    )


class SchoolPostsWithoutVisionApiResponse(ApiResponse):
    """Ответ на запрос получения неувиденных постов"""

    classId: ClassVar[int] = 0x52
    class_id: Literal[0x52, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[SchoolPostsWithoutVisionResult] = Field(
        default=None,
        description="Список последних постов"
    )


class SeeSchoolPostApiResponse(ApiResponse):
    """Ответ на запрос пометки поста как увиденного"""

    classId: ClassVar[int] = 0x53
    class_id: Literal[0x53, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class ClickSchoolPostApiResponse(ApiResponse):
    """Ответ на запрос пометки поста как нажатого"""

    classId: ClassVar[int] = 0x54
    class_id: Literal[0x54, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class ViewSchoolPostResult(ApiBase):
    """Результат запроса пометки поста как просмотренного"""

    classId: ClassVar[int] = 0x55
    class_id: Literal[0x55] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    post: SchoolPost = Field(
        description="Обновленный пост"
    )


class ViewSchoolPostApiResponse(ApiResponse):
    """Ответ на запрос пометки поста как просмотренного"""

    classId: ClassVar[int] = 0x56
    class_id: Literal[0x56, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ViewSchoolPostResult] = Field(
        default=None,
        description="Обновленный пост"
    )


class LikeSchoolPostResult(ApiBase):
    """Результат запроса постановки реакции на посте"""

    classId: ClassVar[int] = 0x57
    class_id: Literal[0x57] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    post: SchoolPost = Field(
        description="Обновленный пост"
    )


class LikeSchoolPostApiResponse(ApiResponse):
    """Ответ на запрос постановки реакции на посте"""

    classId: ClassVar[int] = 0x58
    class_id: Literal[0x58, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[LikeSchoolPostResult] = Field(
        default=None,
        description="Обновленный пост"
    )


class UnlikeSchoolPostResult(ApiBase):
    """Результат запроса удаления реакции на посте"""

    classId: ClassVar[int] = 0x59
    class_id: Literal[0x59] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    post: SchoolPost = Field(
        description="Обновленный пост"
    )


class UnlikeSchoolPostApiResponse(ApiResponse):
    """Ответ на запрос удаления реакции на посте"""

    classId: ClassVar[int] = 0x5A
    class_id: Literal[0x5A, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[UnlikeSchoolPostResult] = Field(
        default=None,
        description="Обновленный пост"
    )
