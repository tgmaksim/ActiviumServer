from typing import ClassVar, Literal, Optional

from pydantic import Field

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['VersionsResult', 'VersionsApiResponse', 'HealthApiResponse', 'CheckSessionResult', 'CheckSessionApiResponse']


class VersionsResult(ApiBase):
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


    class VersionStatus:
        small = 0.1
        minor = 0.3
        new = 0.5
        update = 0.7
        system = 0.9
        global_ = 1

    @classmethod
    def default(cls):
        return cls(
            latestVersionNumber=0,
            latestVersionString="0.0.0",
            date="09.12.2009",
            versionStatusId=cls.VersionStatus.small,
            versionStatus="Мелкие изменения",
            updateLogs="Исправлены ошибки"
        )


class VersionsApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x4
    class_id: Literal[0x4, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[VersionsResult] = Field(
        default=None,
        description="Информация о последней версии приложения"
    )


class HealthApiResponse(ApiResponse):
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
