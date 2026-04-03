from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Query, Request

from ..schemas.settings_schemas import (
    ChildrenApiResponse,
    UpdateFirebaseApiResponse,
    SwitchActiveChildApiResponse,
    StatusEANotificationsApiResponse,
    SwitchEANotificationsApiResponse,
    SwitchMarksNotificationsApiResponse,
    StatusMarksNotificationsApiResponse,
)

from ..services.settings_service import SettingsService
from ...dependencies.services import get_settings_service


__all__ = ['router']

router = APIRouter(prefix='/settings', tags=["Settings"])


@router.get(
    "/getChildren/0",
    summary="Получение списка своих детей",
    description="Получение списка детей, привязанных к пользователю сессии, и активного ребенка. "
                "Необходимо для последующего выбора активного ребенка, с которым ведется взаимодействие",
    response_model=ChildrenApiResponse
)
async def _getChildren0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service)
) -> ChildrenApiResponse:
    request.state.session_id = sessionId
    return await service.getChildren(sessionId)


@router.put(
    "/setActiveChild/0",
    summary="Выбор активного ребенка",
    description="Выбор активного ребенка родителя, с которым ведется взаимодействие",
    response_model=SwitchActiveChildApiResponse
)
async def _setActiveChild0(
        request: Request,
        childId: Annotated[int, Query(description="Идентификатор ребенка, полученный запросом")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service)
) -> SwitchActiveChildApiResponse:
    request.state.session_id = sessionId
    return await service.setActiveChild(sessionId, childId)


@router.get(
    "/getStatusMarksNotifications/0",
    summary="Получение статуса настройки уведомлений о новых оценках",
    description="Получение статуса (включена или выключена) настройки уведомлений о новых оценках для определенного ребенка",
    response_model=StatusMarksNotificationsApiResponse
)
async def _getStatusMarksNotifications0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service),
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None
) -> StatusMarksNotificationsApiResponse:
    request.state.session_id = sessionId
    return await service.getStatusMarksNotifications(sessionId, childId)


@router.put(
    "/switchMarksNotifications/0",
    summary="Изменение уведомлений о новых оценках",
    description="Включение или выключение уведомлений о новых оценках для определенного ребенка",
    response_model=SwitchMarksNotificationsApiResponse
)
async def _switchMarksNotifications0(
        request: Request,
        status: Annotated[bool, Query(description="Новый статус настройки")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service),
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
) -> SwitchMarksNotificationsApiResponse:
    request.state.session_id = sessionId
    return await service.switchMarksNotifications(sessionId, childId, status)


@router.put(
    "/updateFirebase/0",
    summary="Обновление firebase-токена",
    description="Установление или обновление сохраненного firebase-токена для уведомлений",
    response_model=UpdateFirebaseApiResponse
)
async def _updateFirebase0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        firebaseToken: Annotated[str, Query(description="Firebase-токен для отправки уведомлений клиенту", min_length=1, max_length=4096)],
        service: SettingsService = Depends(get_settings_service)
) -> UpdateFirebaseApiResponse:
    request.state.session_id = sessionId
    return await service.update_firebase(sessionId, firebaseToken)


@router.get(
    "/getStatusEANotifications/0",
    summary="Получение статуса настройки уведомлений о внеурочных занятиях",
    description="Получение статуса (включена или выключена) настройки уведомлений о внеурочных занятиях для определенного ребенка",
    response_model=StatusEANotificationsApiResponse
)
async def _getStatusEANotifications0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service),
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None
) -> StatusEANotificationsApiResponse:
    request.state.session_id = sessionId
    return await service.getStatusEANotifications(sessionId, childId)


@router.put(
    "/switchEANotifications/0",
    summary="Изменение уведомлений о внеурочных занятиях",
    description="Включение или выключение уведомлений о внеурочных занятиях для определенного ребенка",
    response_model=SwitchEANotificationsApiResponse
)
async def _switchEANotifications0(
        request: Request,
        status: Annotated[bool, Query(description="Новый статус настройки")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service),
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
) -> SwitchEANotificationsApiResponse:
    request.state.session_id = sessionId
    return await service.switchEANotifications(sessionId, childId, status)
