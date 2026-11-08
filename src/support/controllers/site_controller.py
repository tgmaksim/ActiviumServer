from typing import Annotated, Optional

from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Query, status

from ..services.site_service import SiteService

from ...dependencies.services import get_site_service


__all__ = ['public_router']

public_router = APIRouter(tags=["Site"], include_in_schema=False)
"""Публичный router сайта"""


@public_router.get("/")
async def _root(
        request: Request,
        sessionId: Annotated[Optional[str], Query(description="Идентификатор сессия для статистики и пользовательских взаимодействий на сайте")] = None,
        likesOffset: Annotated[Optional[str], Query(alias='likes-offset', description="Смещение списка отзывов")] = None,
        likesSort: Annotated[Optional[str], Query(alias='likes-sort', description="Тип сортировки отзывов")] = None,
        referral: Annotated[Optional[str], Query(description="Токен реферальной ссылки")] = None,
        service: SiteService = Depends(get_site_service)
):
    likes_offset = None
    try: likes_offset = int(likesOffset)
    except (ValueError, TypeError): pass

    session_id = sessionId or request.cookies.get('session_id')
    request.state.session_id = session_id

    # Query-параметры записываются в cookies и убираются из запроса
    if sessionId is not None:
        response = RedirectResponse(
            url=request.url.remove_query_params('sessionId'),
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie('session_id', session_id, max_age=90 * 24 * 60 * 60, secure=True, httponly=True, samesite='lax')
        return response

    # Query-параметры записываются в cookies и убираются из запроса
    if referral is not None:
        response = RedirectResponse(
            url=request.url.remove_query_params('referral'),
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie('referral', referral, max_age=24 * 60 * 60, secure=True, httponly=True, samesite='lax')
        return response

    template_params = await service.get_root(session_id, likes_offset, likesSort)

    return template_params.to_response(request)


@public_router.head("/")
async def _head_root():
    return HTMLResponse()


@public_router.get("/changelog")
async def _changelog(
        request: Request,
        sessionId: Annotated[Optional[str], Query(description="Идентификатор сессия для статистики и пользовательских взаимодействий на сайте")] = None,
        service: SiteService = Depends(get_site_service)
):
    session_id = sessionId or request.cookies.get('session_id')
    request.state.session_id = session_id

    template_params = await service.get_changelog(session_id)

    return template_params.to_response(request)

@public_router.head("/changelog")
async def _head_changelog():
    return HTMLResponse()


@public_router.get("/privacy")
async def _privacy(
        request: Request,
        sessionId: Annotated[Optional[str], Query(description="Идентификатор сессия для статистики и пользовательских взаимодействий на сайте")] = None,
        service: SiteService = Depends(get_site_service)
):
    session_id = sessionId or request.cookies.get('session_id')
    request.state.session_id = session_id

    template_params = await service.get_privacy(session_id)

    return template_params.to_response(request)

@public_router.head("/privacy")
async def _head_privacy():
    return HTMLResponse()


@public_router.get("/terms")
async def _terms(
        request: Request,
        sessionId: Annotated[Optional[str], Query(description="Идентификатор сессия для статистики и пользовательских взаимодействий на сайте")] = None,
        service: SiteService = Depends(get_site_service)
):
    session_id = sessionId or request.cookies.get('session_id')
    request.state.session_id = session_id

    template_params = await service.get_terms(session_id)

    return template_params.to_response(request)

@public_router.head("/terms")
async def _head_changelog():
    return HTMLResponse()
