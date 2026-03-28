from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Query, Request

from ..schemas.settings_schemas import (
    ChildrenApiResponse,
    UpdateFirebaseApiResponse,
    SwitchActiveChildApiResponse,
    SwitchDnevnikNotificationsApiResponse,
    StatusDnevnikNotificationsApiResponse,
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
    "/getStatusDnevnikNotifications/0",
    summary="Получение статуса настройки уведомлений",
    description="Получение статуса (включена или выключена) настройки уведомлений о новых оценках для определенного ребенка",
    response_model=StatusDnevnikNotificationsApiResponse
)
async def _getStatusDnevnikNotifications0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service),
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None
) -> StatusDnevnikNotificationsApiResponse:
    request.state.session_id = sessionId
    return await service.getStatusDnevnikNotifications(sessionId, childId)


@router.put(
    "/switchDnevnikNotifications/0",
    summary="Изменение уведомлений",
    description="Включение или выключение уведомлений о новых оценках для определенного ребенка",
    response_model=SwitchDnevnikNotificationsApiResponse
)
async def _switchDnevnikNotifications0(
        request: Request,
        status: Annotated[bool, Query(description="Новый статус настройки")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SettingsService = Depends(get_settings_service),
        childId: Annotated[Optional[int], Query(description="Идентификатор ребенка")] = None,
) -> SwitchDnevnikNotificationsApiResponse:
    request.state.session_id = sessionId
    return await service.switchDnevnikNotifications(sessionId, childId, status)


@router.put(
    "/updateFirebase/0",
    summary="Обновление firebase-токена",
    description="Установление или обновление сохраненного firebase-токена для уведомлений",
    response_model=UpdateFirebaseApiResponse
)
async def _updateFirebase0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        firebaseToken: Annotated[Optional[str], Query(description="Firebase-токен для отправки уведомлений клиенту", min_length=1, max_length=4096)] = None,
        service: SettingsService = Depends(get_settings_service)
) -> UpdateFirebaseApiResponse:
    request.state.session_id = sessionId
    return await service.update_firebase(sessionId, firebaseToken)
