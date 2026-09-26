from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from ..schemas.settings_schemas import (
    ChildrenApiResponse,
    ReferralParamsApiResponse,
    UpdateFirebaseApiResponse,
    SwitchActiveChildApiResponse,
    ReferralParamsApiResponse0x46,
    StatusEANotificationsApiResponse,
    SwitchEANotificationsApiResponse,
    SwitchMarksNotificationsApiResponse,
    StatusMarksNotificationsApiResponse,
    HideExtracurricularActivityApiResponse,
)

from ...dependencies.auth import get_session_id
from ..services.settings_service import SettingsService
from ...dependencies.services import get_settings_service


__all__ = ['router']

router = APIRouter(prefix='/settings', tags=["Settings"])
"""Router группы запросов settings"""


@router.get(
    "/getChildren/0",
    summary="Получение списка своих детей",
    description="Получение списка детей, привязанных к пользователю сессии, и активного ребенка. "
                "Необходимо для последующего выбора активного ребенка, с которым ведется взаимодействие",
    response_model=ChildrenApiResponse
)
async def _getChildren0(
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service)
) -> ChildrenApiResponse:
    return await service.getChildren(sessionId)


@router.put(
    "/setActiveChild/0",
    summary="Выбор активного ребенка",
    description="Выбор активного ребенка родителя, с которым ведется взаимодействие",
    response_model=SwitchActiveChildApiResponse
)
async def _setActiveChild0(
        childId: Annotated[int, Query(description="Идентификатор ребенка, полученный запросом")],
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service)
) -> SwitchActiveChildApiResponse:
    return await service.setActiveChild(sessionId, childId)


@router.get(
    "/getStatusMarksNotifications/0",
    summary="Получение статуса настройки уведомлений о новых оценках",
    description="Получение статуса (включена или выключена) настройки уведомлений о новых оценках для определенного ребенка",
    response_model=StatusMarksNotificationsApiResponse
)
async def _getStatusMarksNotifications0(
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service)
) -> StatusMarksNotificationsApiResponse:
    return await service.getStatusMarksNotifications(sessionId, childId)


@router.put(
    "/switchMarksNotifications/0",
    summary="Изменение уведомлений о новых оценках",
    description="Включение или выключение уведомлений о новых оценках для определенного ребенка",
    response_model=SwitchMarksNotificationsApiResponse
)
async def _switchMarksNotifications0(
        status: Annotated[bool, Query(description="Новый статус настройки")],
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service)
) -> SwitchMarksNotificationsApiResponse:
    return await service.switchMarksNotifications(sessionId, childId, status)


@router.put(
    "/updateFirebase/0",
    summary="Обновление firebase-токена",
    description="Установление или обновление сохраненного firebase-токена для уведомлений",
    response_model=UpdateFirebaseApiResponse
)
async def _updateFirebase0(
        firebaseToken: Annotated[str, Query(description="Firebase-токен для отправки уведомлений клиенту", min_length=1, max_length=4096)],
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service)
) -> UpdateFirebaseApiResponse:
    return await service.update_firebase(sessionId, firebaseToken)


@router.get(
    "/getStatusEANotifications/0",
    summary="Получение статуса настройки уведомлений о внеурочных занятиях",
    description="Получение статуса (включена или выключена) настройки уведомлений о внеурочных занятиях для определенного ребенка",
    response_model=StatusEANotificationsApiResponse
)
async def _getStatusEANotifications0(
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service)
) -> StatusEANotificationsApiResponse:
    return await service.getStatusEANotifications(sessionId, childId)


@router.put(
    "/switchEANotifications/0",
    summary="Изменение уведомлений о внеурочных занятиях",
    description="Включение или выключение уведомлений о внеурочных занятиях для определенного ребенка",
    response_model=SwitchEANotificationsApiResponse
)
async def _switchEANotifications0(
        status: Annotated[bool, Query(description="Новый статус настройки")],
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service),
) -> SwitchEANotificationsApiResponse:
    return await service.switchEANotifications(sessionId, childId, status)


@router.get(
    "/getReferralParams/0",
    summary="Получение параметров реферальной программы",
    description="Получение количества приглашенных пользователей, ссылки для приглашения и имени, который пригласил пользователя",
    response_model=ReferralParamsApiResponse0x46,
    deprecated=True  # Устарела с версии API 1.14.0
)
async def _getReferralParams0(
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service),
) -> ReferralParamsApiResponse0x46:
    return await service.getReferralParams(sessionId, api=0)


@router.get(
    "/getReferralParams/1",  # Начиная с версии API 1.14.0
    summary="Получение параметров реферальной программы",
    description="Получение количества приглашенных пользователей, ссылки для приглашения и имени, который пригласил пользователя",
    response_model=ReferralParamsApiResponse
)
async def _getReferralParams1(
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service),
) -> ReferralParamsApiResponse:
    return await service.getReferralParams(sessionId, api=1)


@router.put(
    "/hideExtracurricularActivity/0",
    summary="Скрытие определенного внеурочного занятия",
    description="Скрытие уведомлений с напоминанием об определенном внеурочном занятии",
    response_model=HideExtracurricularActivityApiResponse
)
async def _hideExtracurricularActivity0(
        subject: Annotated[str, Query(description="Название предмета внеурочного занятия", min_length=1, max_length=32)],
        place: Annotated[str, Query(description="Место проведения (кабинет) внеурочного занятия", min_length=1, max_length=32)],
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
        sessionId: str = Depends(get_session_id),
        service: SettingsService = Depends(get_settings_service),
) -> HideExtracurricularActivityApiResponse:
    return await service.hideExtracurricularActivity(sessionId, childId, subject, place)
