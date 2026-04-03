from pydantic import Field
from typing import ClassVar, Literal, Optional

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Child', 'ChildrenResult', 'ChildrenApiResponse', 'SwitchActiveChildApiResponse', 'StatusMarksNotificationsResult',
           'StatusMarksNotificationsApiResponse', 'SwitchMarksNotificationsApiResponse', 'UpdateFirebaseApiResponse',
           'StatusEANotificationsResult', 'StatusEANotificationsApiResponse', 'SwitchEANotificationsApiResponse']


class Child(ApiBase):
    """Ребенок"""

    classId: ClassVar[int] = 0x21
    class_id: Literal[0x21] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    childId: int = Field(
        description="Идентификатор ребенка, который необходим для выбора активного",
        examples=[0]
    )
    name: str = Field(
        description="Имя ребенка для показа в клиенте",
        examples=["Максим"]
    )


class ChildrenResult(ApiBase):
    """Результат запроса получения своих детей"""

    classId: ClassVar[int] = 0x22
    class_id: Literal[0x22] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    children: list[Child] = Field(
        description="Список детей, привязанных к пользователю сессии"
    )
    activeChildId: int = Field(
        description="Идентификатор активного ребенка",
        examples=[0]
    )


class ChildrenApiResponse(ApiResponse):
    """Ответ на запрос получения своих детей"""

    classId: ClassVar[int] = 0x23
    class_id: Literal[0x23, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ChildrenResult] = Field(
        default=None,
        description="Данные о детях пользователя"
    )


class SwitchActiveChildApiResponse(ApiResponse):
    """Ответ на запрос изменения активного ребенка родителя"""

    classId: ClassVar[int] = 0x24
    class_id: Literal[0x24, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ChildrenResult] = Field(
        default=None,
        description="Данные о детях пользователя"
    )


class StatusMarksNotificationsResult(ApiBase):
    """Результат запроса получения статуса настройки уведомлений о новых оценках"""

    classId: ClassVar[int] = 0x25
    class_id: Literal[0x25] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    status: bool = Field(
        description="Статус функции уведомлений о новых оценках"
    )


class StatusMarksNotificationsApiResponse(ApiResponse):
    """Ответ на запрос получения статуса настройки уведомлений о новых оценках"""

    classId: ClassVar[int] = 0x26
    class_id: Literal[0x26, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: StatusMarksNotificationsResult = Field(
        default=None,
        description="Статус настройки уведомлений о новых уведомлениях"
    )


class SwitchMarksNotificationsApiResponse(ApiResponse):
    """Ответ на запрос изменения настройки уведомлений о новых оценках"""

    classId: ClassVar[int] = 0x27
    class_id: Literal[0x27, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class UpdateFirebaseApiResponse(ApiResponse):
    """Ответ на запрос обновления firebase-токена для работы уведомлений"""

    classId: ClassVar[int] = 0x28
    class_id: Literal[0x28, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class StatusEANotificationsResult(ApiBase):
    """Результат запроса получения статуса настройки уведомлений о внеурочных занятиях"""

    classId: ClassVar[int] = 0x3B
    class_id: Literal[0x3B] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    status: bool = Field(
        description="Статус функции уведомлений о внеурочных занятиях"
    )


class StatusEANotificationsApiResponse(ApiResponse):
    """Ответ на запрос получения статуса настройки уведомлений о внеурочных занятиях"""

    classId: ClassVar[int] = 0x3C
    class_id: Literal[0x3C, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: StatusEANotificationsResult = Field(
        default=None,
        description="Статус настройки уведомлений о внеурочных занятиях"
    )


class SwitchEANotificationsApiResponse(ApiResponse):
    """Ответ на запрос изменения настройки уведомлений о внеурочных занятиях"""

    classId: ClassVar[int] = 0x3D
    class_id: Literal[0x3D, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )
