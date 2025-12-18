from pydantic import Field
from typing import Optional, ClassVar, Literal

from api.entities import ApiBase, ApiRequest, ApiResponse, ApiSession


__all__ = ['LoginApiRequest', 'LoginResult', 'LoginApiResponse', 'CheckSessionApiRequest', 'CheckSessionResult',
           'CheckSessionApiResponse']


class LoginApiRequest(ApiRequest):
    """Запрос на генерацию сессии и получение ссылки для ее авторизации"""

    classId: ClassVar[int] = 0x00000007
    class_id: Literal[0x00000007] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: Optional[ApiSession] = Field(
        description="Данные сессии для повторной авторизации без создания новой (может быть отклонено и создана новая)"
    )


class LoginResult(ApiBase):
    """Результат запроса на генерацию сессии и получение ссылки для ее авторизации"""

    classId: ClassVar[int] = 0x00000008
    class_id: Literal[0x00000008] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    loginUrl: str = Field(
        description="Ссылка для авторизации сессии (нужно открыть в браузере пользователя)",
        examples=["https://login.dnevnik.ru/oauth2"]
    )
    session: str = Field(
        description="Строковый идентификатор сессии для персонализированных запросов",
        min_length=1,
        max_length=64,
        pattern="[a-zA-Z0-9]+",
        examples=["55e5bccb595d10beb8d5bf85d447dff2c411275d3ce9f2823afb3a56407f8afe"]
    )


class LoginApiResponse(ApiResponse):
    """Ответ на запрос на генерацию сессии и получение ссылки для ее авторизации"""

    classId: ClassVar[int] = 0x00000009
    class_id: Literal[0x00000009] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[LoginResult] = Field(
        default=None,
        description="Данные для авторизации пользователя"
    )


class CheckSessionApiRequest(ApiRequest):
    """Запрос для проверки сессии на существование и авторизацию"""

    classId: ClassVar[int] = 0x0000000A
    class_id: Literal[0x0000000A] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: ApiSession = Field(
        description="Данные для проверки сессии"
    )


class CheckSessionResult(ApiBase):
    """Результат запроса для проверки сессии на существование и авторизацию"""

    classId: ClassVar[int] = 0x0000000B
    class_id: Literal[0x0000000B] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    exists: bool = Field(
        description="Существование сессии"
    )
    auth: bool = Field(
        description="Авторизация сессии в сервисе дневника.ру"
    )


class CheckSessionApiResponse(ApiResponse):
    """Ответ на запрос для проверки сессии на существование и авторизацию"""

    classId: ClassVar[int] = 0x0000000C
    class_id: Literal[0x0000000C] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[CheckSessionResult] = Field(
        default=None,
        description="Данные о сессии: существует ли она и статус ее авторизации в сервисе дневника.ру"
    )
