from typing import ClassVar, Literal, Optional

from pydantic import Field

from .error_schema import ApiError
from ..schemas.base_schema import ApiBase


__all__ = ['ApiResponse']


class ApiResponse(ApiBase):
    classId: ClassVar[int] = 0x2
    class_id: Literal[0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    status: bool = Field(
        default=True,
        description="Статус выполненного запроса",
        examples=[True, False]
    )
    error: Optional[ApiError] = Field(
        default=None,
        description="Объект API-ошибки"
    )
    answer: Optional[ApiBase] = Field(
        default=None,
        description="Ответ в случае успешной обработки"
    )
