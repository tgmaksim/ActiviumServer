from pydantic import Field
from typing import ClassVar, Literal, Optional

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Child', 'ChildrenResult', 'ChildrenApiResponse', 'SwitchActiveChildApiResponse', 'StatusDnevnikNotificationsResult',
           'StatusDnevnikNotificationsApiResponse', 'SwitchDnevnikNotificationsApiResponse', 'UpdateFirebaseApiResponse']


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

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class StatusDnevnikNotificationsResult(ApiBase):
    """Результат запроса получения статуса настройки уведомлений"""

    classId: ClassVar[int] = 0x25
    class_id: Literal[0x25] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    status: bool = Field(
        description="Статус функции уведомлений о новых оценках"
    )


class StatusDnevnikNotificationsApiResponse(ApiResponse):
    """Ответ на запрос получения статуса настройки уведомлений"""

    classId: ClassVar[int] = 0x26
    class_id: Literal[0x26, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: StatusDnevnikNotificationsResult = Field(
        default=None,
        description="Статус настройки уведомлений"
    )


class SwitchDnevnikNotificationsApiResponse(ApiResponse):
    """Ответ на запрос изменения настройки уведомлений"""

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
