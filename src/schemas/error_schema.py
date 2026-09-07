from typing import ClassVar, Literal, Optional

from pydantic import Field

from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..schemas.base_schema import ApiBase
from ..api.api_exception import ApiException


__all__ = ['ApiError']


class ApiError(ApiBase):
    """Класс API-ошибок в ответах"""

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

    def exception(self, status_code: int = HTTP_500_INTERNAL_SERVER_ERROR) -> ApiException:
        return ApiException(error=self, status_code=status_code)
