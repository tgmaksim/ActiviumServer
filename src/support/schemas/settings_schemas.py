from pydantic import Field
from typing import ClassVar, Literal, Optional

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Child', 'ChildrenResult', 'ChildrenApiResponse', 'SwitchActiveChildApiResponse', 'StatusMarksNotificationsResult',
           'StatusMarksNotificationsApiResponse', 'SwitchMarksNotificationsApiResponse', 'UpdateFirebaseApiResponse',
           'StatusEANotificationsResult', 'StatusEANotificationsApiResponse', 'SwitchEANotificationsApiResponse',
           'ReferralParamsResult0x45', 'ReferralParamsApiResponse0x46', 'ReferralParamsResult', 'ReferralParamsApiResponse',
           'HideExtracurricularActivityApiResponse']


class Child(ApiBase):
    """Ребенок (профиль)"""

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


class ReferralParamsResult0x45(ApiBase):  # До версии API 1.14.0
    """Результат запроса получения параметров реферальной программы для пользователя"""

    classId: ClassVar[int] = 0x45
    class_id: Literal[0x45, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    meReferralName: Optional[str] = Field(
        description="Имя пользователя, который пригласил"
    )
    referralsCount: int = Field(
        description="Количество приглашенных пользователей"
    )
    referralUrl: str = Field(
        description="Реферальная ссылка для приглашения"
    )


class ReferralParamsApiResponse0x46(ApiResponse):  # До версии API 1.14.0
    """Ответ на запрос получения параметров реферальной программы для пользователя"""

    classId: ClassVar[int] = 0x46
    class_id: Literal[0x46, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ReferralParamsResult0x45] = Field(
        default=None,
        description="Параметры реферальной программы для пользователя"
    )


class ReferralParamsResult(ApiBase):  # Начиная с версии API 1.14.0
    """Результат запроса получения параметров реферальной программы для пользователя"""

    classId: ClassVar[int] = 0x5F
    class_id: Literal[0x5F, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    meReferralName: Optional[str] = Field(
        description="Имя пользователя, который пригласил"
    )
    referralsCount: int = Field(
        description="Количество приглашенных пользователей"
    )
    isParent: bool = Field(
        description="Является ли пользователь родителем"
    )
    countActiveRelatives: int = Field(
        description="Сколько детей/родителей зарегистрированы в сервисе"
    )
    countRelatives: int = Field(
        description="Общее количество связанных детей/родителей в Дневнике.ру"
    )
    referralUrl: str = Field(
        description="Реферальная ссылка для приглашения"
    )


class ReferralParamsApiResponse(ApiResponse):  # Начиная с версии API 1.14.0
    """Ответ на запрос получения параметров реферальной программы для пользователя"""

    classId: ClassVar[int] = 0x60
    class_id: Literal[0x60, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ReferralParamsResult] = Field(
        default=None,
        description="Параметры реферальной программы для пользователя"
    )


class HideExtracurricularActivityApiResponse(ApiResponse):
    """Ответ на запрос скрытия уведомлений об определенном внеурочном занятии"""

    classId: ClassVar[int] = 0x65
    class_id: Literal[0x65, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )
