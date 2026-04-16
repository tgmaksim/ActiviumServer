from typing import Annotated, Optional

from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Query, status

from ..services.site_service import SiteService

from ...dependencies.templates import get_templates
from ...dependencies.services import get_site_service


__all__ = ['router']

router = APIRouter()


@router.get("/", include_in_schema=False)
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

    if sessionId is not None:
        response = RedirectResponse(
            url=request.url.remove_query_params('sessionId'),
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie('session_id', session_id, max_age=30 * 24 * 60 * 60, secure=True, httponly=True)
        return response

    if referral is not None:
        response = RedirectResponse(
            url=request.url.remove_query_params('referral'),
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie('referral', referral, max_age=30 * 24 * 60 * 60, secure=True, httponly=True)
        return response

    template_params = await service.get_root(session_id, likes_offset, likesSort)

    templates = get_templates()
    response = templates.TemplateResponse(
        request=request,
        status_code=template_params.status_code,
        name=template_params.name,
        context=template_params.context
    )

    response.set_cookie('session_id', session_id, max_age=30 * 24 * 60 * 60, secure=True, httponly=True)
    if template_params.cookies:
        for cookie in template_params.cookies:
            response.set_cookie(**cookie)

    return response


@router.head("/", include_in_schema=False)
async def _head_root():
    return HTMLResponse()
