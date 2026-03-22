from typing import ClassVar, Literal, Optional

from pydantic import Field

from ..schemas.base_schema import ApiBase


__all__ = ['ApiError']


class ApiError(ApiBase):
    classId: ClassVar[int] = 0x1
    class_id: Literal[0x1] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    type: str = Field(
        description="Определенный тип ошибки из возможных",
        examples=[
            "ValidationError",
            "UnauthorizedError",
            "InvalidApiKeyError",
            "InternalServerError",
            "ApiMethodNotFoundError",
            "IntervalTooLong",
            "ValueError",
            "ReviewNotFoundError",
            "ReviewLikeNotFoundError",
        ]
    )
    errorMessage: Optional[str] = Field(
        default=None,
        description="Сообщение об ошибке для показа пользователю коротким оповещением",
        examples=["Сервер временно не доступен"]
    )
