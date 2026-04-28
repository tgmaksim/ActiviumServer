from typing import ClassVar, Literal, Optional

from pydantic import Field

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['VersionsResult0x3', 'VersionsApiResponse0x4', 'HealthApiResponse', 'CheckSessionResult', 'CheckSessionApiResponse',
           'Message', 'InformationResult', 'InformationApiResponse', 'VersionsResult', 'VersionsApiResponse']


class VersionsResult0x3(ApiBase):  # До версии API 1.0.12.6
    """Результат запроса получения новой версии приложения"""

    classId: ClassVar[int] = 0x3
    class_id: Literal[0x3] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    latestVersionNumber: int = Field(
        description="Последняя доступная версия (номер сборки) приложения",
        examples=[500]
    )
    latestVersionString: str = Field(
        description="Последняя доступная версия приложения",
        examples=["0.3.0-beta"]
    )
    date: str = Field(
        description="Дата выпуска последней доступной версии приложения",
        examples=["09.12.2009"]
    )
    versionStatusId: float = Field(
        description="Числовой статус новой версии, означающий важность обновления",
        examples=[0.1, 0.3, 0.5, 0.7, 0.9, 1]
    )
    versionStatus: str = Field(
        description="Статус новой версии, означающий важность обновления",
        examples=["Мелкие изменения", "Небольшие улучшения", "Новая(ые) функция(и)", "Требуется обновление",
                  "Важные системные изменения", "Глобальное обновление"]
    )
    updateLogs: str = Field(
        description="Изменения в последней версии приложения (latestVersion), которые можно показать пользователю",
        examples=["1. Добавлена новая функция\n2. Исправлены ошибки"]
    )


class VersionsApiResponse0x4(ApiResponse):  # До версии API 1.0.12.6
    """Ответ на запрос получения новой версии приложения"""

    classId: ClassVar[int] = 0x4
    class_id: Literal[0x4, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[VersionsResult0x3] = Field(
        default=None,
        description="Информация о последней версии приложения"
    )


class VersionsResult(ApiBase):  # Начиная с версии API 1.1.0
    """Результат запроса получения новой версии приложения"""

    classId: ClassVar[int] = 0x43
    class_id: Literal[0x43] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    latestVersionNumber: int = Field(
        description="Последняя доступная версия (номер сборки) приложения",
        examples=[500]
    )
    latestVersionString: str = Field(
        description="Последняя доступная версия приложения",
        examples=["0.3.0-beta"]
    )
    date: str = Field(
        description="Дата выпуска последней доступной версии приложения",
        examples=["09.12.2009"]
    )
    versionStatusId: float = Field(
        description="Числовой статус новой версии, означающий важность обновления",
        examples=[0.1, 0.3, 0.5, 0.7, 0.9, 1]
    )
    versionStatus: str = Field(
        description="Статус новой версии, означающий важность обновления",
        examples=["Мелкие изменения", "Небольшие улучшения", "Новая(ые) функция(и)", "Требуется обновление",
                  "Важные системные изменения", "Глобальное обновление"]
    )
    info: Optional[str] = Field(
        description="Информационное сообщение, которое нужно показать пользователю",
        examples=["Вышла новая версия приложение. Требуется обновить его"]
    )
    updateLogs: str = Field(
        description="Изменения в последней версии приложения (latestVersion), которые можно показать пользователю",
        examples=["1. Добавлена новая функция\n2. Исправлены ошибки"]
    )

    class VersionStatus:
        small = 0.1
        minor = 0.3
        new = 0.5
        update = 0.7
        system = 0.9
        global_ = 1


class VersionsApiResponse(ApiResponse):  # Начиная с версии API 1.1.0
    """Ответ на запрос получения новой версии приложения"""

    classId: ClassVar[int] = 0x44
    class_id: Literal[0x44, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[VersionsResult] = Field(
        default=None,
        description="Информация о последней версии приложения"
    )


class HealthApiResponse(ApiResponse):
    """Ответ на запрос проверки работоспособности сервера"""

    classId: ClassVar[int] = 0x5
    class_id: Literal[0x5, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class CheckSessionResult(ApiBase):
    """Результат запроса для проверки сессии на существование и авторизацию"""

    classId: ClassVar[int] = 0x6
    class_id: Literal[0x6] = Field(
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

    classId: ClassVar[int] = 0x7
    class_id: Literal[0x7, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[CheckSessionResult] = Field(
        default=None,
        description="Данные о сессии: существует ли она и статус ее авторизации в сервисе дневника.ру"
    )


class Message(ApiBase):
    """Информационное сообщение"""

    classId: ClassVar[int] = 0x40
    class_id: Literal[0x40, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    title: str = Field(
        description="Заголовок сообщения"
    )
    text: str = Field(
        description="Текст сообщения"
    )


class InformationResult(ApiBase):
    """Результат запроса получения информационных сообщений"""

    classId: ClassVar[int] = 0x41
    class_id: Literal[0x41, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    messages: list[Message] = Field(
        description="Информационные сообщения для пользователя, если есть"
    )


class InformationApiResponse(ApiResponse):
    """Ответ на запрос получения информационных сообщений"""

    classId: ClassVar[int] = 0x42
    class_id: Literal[0x42, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[InformationResult] = Field(
        default=None,
        description="Различная информация для показа пользователю"
    )
