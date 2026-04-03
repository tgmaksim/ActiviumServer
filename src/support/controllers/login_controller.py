from typing import Annotated, Optional

from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Query, Depends

from ..schemas.login_schemas import LoginApiResponse
from ..schemas.status_schemas import CheckSessionApiResponse

from ..services.login_service import LoginService
from ...dependencies.templates import get_templates
from ...dependencies.services import get_login_service


__all__ = ['router', 'public_router']

router = APIRouter(prefix='/login', tags=["Login"])
public_router = APIRouter(prefix='/login', tags=["Login"], include_in_schema=False)


@router.post(
    "/login/0",
    summary="Авторизация",
    description="Создание сессии для взаимодействия с API. Возвращает ссылку для авторизации через дневник.ру",
    response_model=LoginApiResponse
)
async def _login0(
        request: Request,
        firebaseToken: Annotated[str, Query(description="Firebase-токен для отправки уведомлений клиенту", min_length=1, max_length=4096)],
        sessionId: Annotated[Optional[str], Query(description="Ранее использованный идентификатор сессии для повторной авторизации", min_length=1, max_length=32)] = None,
        service: LoginService = Depends(get_login_service)
) -> LoginApiResponse:
    request.state.session_id = sessionId
    return await service.login(sessionId, firebaseToken)


@public_router.get(
    "/authSession",
    summary="Первичное и вторичное получение параметров от дневника.ру. Авторизация сессии",
    description="После авторизации дневник.ру перенаправит пользователя в данный метод, а здесь будет возвращен HTML. "
                "JS возьмет полученные параметры из url#hash и отправит в url?query. После вторичного получения "
                "параметров от дневника.ру они используются для авторизации",
    response_class=HTMLResponse
)
async def _authSession(
        request: Request,
        access_token: Annotated[Optional[str], Query(description="Токен для взаимодействия с дневником.ру от имени пользователя", min_length=1, max_length=64)] = None,
        state: Annotated[Optional[str], Query(description="Дополнительные параметры от дневника.ру (внутренний идентификатор сессии sessionId)", min_length=1, max_length=32)] = None,
        service: LoginService = Depends(get_login_service)
) -> HTMLResponse:
    request.state.session_id = state
    if access_token is not None and state is not None:
        template_params = await service.secondAuthSession(access_token, state)
    else:
        template_params = await service.firstAuthSession()

    templates = get_templates()
    response = templates.TemplateResponse(
        request=request,
        name=template_params.name,
        status_code=template_params.status_code,
        context=template_params.context
    )

    if template_params.cookies:
        response.set_cookie(**template_params.cookies)

    return response


@router.get(
    "/checkSession/0",
    summary="Проверка сессии",
    description="Проверка существования сессии и ее авторизации в сервисе дневник.ру",
    response_model=CheckSessionApiResponse
)
async def _checkSession(
        request: Request,
        sessionId: Annotated[str, Query(description="Идентификатор сессии для проверки", min_length=1, max_length=32)],
        service: LoginService = Depends(get_login_service)
) -> CheckSessionApiResponse:
    request.state.session_id = sessionId
    return await service.checkSession(sessionId)
