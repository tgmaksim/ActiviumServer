import datetime

from typing import ClassVar, Literal, Optional

from pydantic import Field, field_serializer

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Review', 'CreateReviewApiResponse', 'MyReviewResult', 'MyReviewApiResponse', 'DeleteReviewApiResponse',
           'ReviewsResult', 'ReviewsApiResponse', 'LikeReviewResult', 'LikeReviewApiResponse', 'DeleteReviewLikeResult',
           'DeleteReviewLikeApiResponse']


class Review(ApiBase):
    classId: ClassVar[int] = 0x29
    class_id: Literal[0x29] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    reviewId: int = Field(
        description="Идентификатор отзыва",
        ge=1,
        le=2**63-1
    )
    name: str = Field(
        description="Имя автора отзыва"
    )
    stars: int = Field(
        description="Оценка отзыва",
        ge=1,
        le=5
    )
    text: Optional[str] = Field(
        description="Текст отзыва",
        min_length=1,
        max_length=256
    )
    likes: int = Field(
        description="Количество реакций на отзыв",
        ge=0
    )
    createdAt: datetime.datetime = Field(
        description="Дата и время написания отзыва"
    )
    isUpdated: bool = Field(
        description="Отзыв был изменен после написания"
    )

    @field_serializer('createdAt')
    def serialize_dt(self, dt: datetime.datetime, _info):
        return dt.replace(microsecond=0).isoformat()


class MyReviewResult(ApiBase):
    classId: ClassVar[int] = 0x2A
    class_id: Literal[0x2A] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    review: Optional[Review] = Field(
        description="Отзыв написанный пользователем, если есть"
    )
    onModeration: bool = Field(
        description="Отзыв на модерации"
    )


class CreateReviewApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x2B
    class_id: Literal[0x2B, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[MyReviewResult] = Field(
        default=None,
        description="Отзыв, который создан"
    )


class MyReviewApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x2C
    class_id: Literal[0x2C, 0x2] = Field(
        default=classId,
        description="Идентификатор класса"
    )

    answer: Optional[MyReviewResult] = Field(
        default=None,
        description="Отзыв, написанный пользователем, если есть"
    )


class DeleteReviewApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x2D
    class_id: Literal[0x2D, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class ReviewsResult(ApiBase):
    classId: ClassVar[int] = 0x2E
    class_id: Literal[0x2E] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    reviews: list[Review] = Field(
        description="Список отзывов по запросу"
    )
    nextOffset: Optional[int] = Field(
        description="Смещение для показа следующих отзывов",
        ge=0
    )


class ReviewsApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x2F
    class_id: Literal[0x2F, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ReviewsResult] = Field(
        default=None,
        description="Отзывы"
    )


class LikeReviewResult(ApiBase):
    classId: ClassVar[int] = 0x30
    class_id: Literal[0x30] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    review: Review = Field(
        description="Данные отзыва после постановки реакции"
    )


class LikeReviewApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x31
    class_id: Literal[0x31, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[LikeReviewResult] = Field(
        default=None,
        description="Данные отзыва после постановки лайка"
    )


class DeleteReviewLikeResult(ApiBase):
    classId: ClassVar[int] = 0x32
    class_id: Literal[0x32] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    review: Review = Field(
        description="Данные отзыва после удаления реакции"
    )


class DeleteReviewLikeApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x33
    class_id: Literal[0x33, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[DeleteReviewLikeResult] = Field(
        default=None,
        description="Данные отзыва после удаления реакции"
    )
