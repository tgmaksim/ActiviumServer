from pydantic import Field
from typing import Optional, ClassVar, Literal

from api.entities import ApiBase, ApiRequest, ApiResponse


__all__ = ['VersionsApiRequest0x00000004', 'VersionsInputData', 'VersionsApiRequest', 'VersionsResult',
           'VersionsApiResponse']


class VersionsInputData(ApiBase):
    """Входные данные для запроса последней версии приложения"""

    classId: ClassVar[int] = 0x00000024
    class_id: Literal[0x00000024] = Field(
        default=classId,
        alias="classId",
        description="Идентификатор класса"
    )

    versionNumber: int = Field(
        description="Номер сборки приложения"
    )


class VersionsApiRequest0x00000004(ApiRequest):
    """Запрос данных о последней версии приложения устаревшая версия"""

    classId: ClassVar[int] = 0x00000004
    class_id: Literal[0x00000004] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: None = None


class VersionsApiRequest(ApiRequest):
    """Запрос данных о последней версии приложения"""

    classId: ClassVar[int] = 0x00000025
    class_id: Literal[0x00000025] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: VersionsInputData = Field(
        description="Данные версии приложения"
    )


class VersionsResult(ApiBase):
    """Результат запроса данных о последней версии приложения"""

    classId: ClassVar[int] = 0x00000005
    class_id: Literal[0x00000005] = Field(
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
    versionStatus: str = Field(
        description="Статус новой версии, означающий важность обновления",
        examples=["Требуется обновить"]
    )
    updateLogs: str = Field(
        description="Изменения в последней версии приложения (latestVersion), которые можно показать пользователю",
        examples=["1. Добавлена новая функция\n2. Исправлены ошибки"]
    )

    @classmethod
    def default(cls):
        return cls(
            latestVersionNumber=0,
            latestVersionString="0.0.0",
            date="09.12.2009",
            versionStatus="Новая версия",
            updateLogs="Исправлены ошибки"
        )


class VersionsApiResponse(ApiResponse):
    """Ответ на запрос данных о последней версии приложения"""

    classId: ClassVar[int] = 0x00000006
    class_id: Literal[0x00000006] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[VersionsResult] = Field(
        default=None,
        description="Информация о последней версии приложения"
    )
