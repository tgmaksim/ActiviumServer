from pydantic import BaseModel, Field
from typing import Optional, ClassVar, Literal


__all__ = ['BaseModel', 'ApiBase', 'ApiRequest', 'ApiResponse', 'ApiError', 'ApiSession']


class ApiBase(BaseModel):
    """Базовый класс для любой API-сущности"""

    classId: ClassVar[int] = 0x00000000  # Абстрактный класс
    class_id: Literal[0x00000000] = Field(
        alias='classId',  # Для проверки входящего classId
        description="Идентификатор класса"
    )


class ApiRequest(ApiBase):
    """Базовый класс всех API-запросов"""

    classId: ClassVar[int] = 0x00000000  # Абстрактный класс
    class_id: Literal[0x00000000] = Field(
        alias='classId',
        description="Идентификатор класса"
    )

    apiKey: str = Field(
        description="API-ключ для взаимодействия с сервером",
        min_length=1,
        max_length=32,
        pattern="[a-zA-Z0-9]+",
        examples=["d4124513c7b6c64510085036561edb37"]
    )
    data: Optional[ApiBase] = Field(
        description="Входные данные запроса"
    )


class ApiError(ApiBase):
    """Базовый класс для всех ошибок в API-ответах"""

    classId: ClassVar[int] = 0x00000001
    class_id: Literal[0x00000001] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    type: str = Field(
        description="Определенный тип ошибки из возможных",
        examples=["InternationalServerError", "InvalidApiKey", "Unauthorized", "ValidationError"]
    )
    errorMessage: Optional[str] = Field(
        default=None,
        description="Сообщение об ошибке для показа пользователю коротким оповещением",
        examples=["Сервер временно не доступен"]
    )


class ApiResponse(ApiBase):
    """Базовый класс всех API-ответов"""

    classId: ClassVar[int] = 0x00000002
    class_id: Literal[0x00000002] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    status: bool = Field(
        default=True,
        description="Статус выполненного запроса",
        examples=[True]
    )
    error: Optional[ApiError] = Field(
        default=None,
        description="Объект API-ошибки"
    )
    answer: Optional[ApiBase] = Field(
        default=None,
        description="Ответ в случае успешной обработки"
    )


class ApiSession(ApiBase):
    """Данные сессии"""

    classId: ClassVar[int] = 0x00000003
    class_id: Literal[0x00000003] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    session: str = Field(
        description="Строковый идентификатор сессии для персонализированных запросов",
        min_length=1,
        max_length=64,
        pattern="[a-zA-Z0-9]+",
        examples=["55e5bccb595d10beb8d5bf85d447dff2c411275d3ce9f2823afb3a56407f8afe"]
    )
