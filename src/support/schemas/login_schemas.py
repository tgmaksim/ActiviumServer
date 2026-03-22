from typing import ClassVar, Literal, Optional

from pydantic import Field

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['LoginResult', 'LoginApiResponse']


class LoginResult(ApiBase):
    classId: ClassVar[int] = 0x8
    class_id: Literal[0x8] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    loginUrl: str = Field(
        description="Ссылка для авторизации сессии (нужно открыть в браузере пользователя)",
        examples=["https://login.dnevnik.ru/oauth2"]
    )
    sessionId: str = Field(
        description="Строковый идентификатор сессии для персонализированных запросов",
        min_length=1,
        max_length=64,
        pattern="[0-9a-f]+",
        examples=["55e5bccb595d10beb8d5bf85d447dff2c411275d3ce9f2823afb3a56407f8afe"]
    )


class LoginApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x9
    class_id: Literal[0x9, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[LoginResult] = Field(
        default=None,
        description="Данные для авторизации пользователя"
    )
