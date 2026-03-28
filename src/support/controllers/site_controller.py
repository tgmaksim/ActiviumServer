from typing import Annotated, Optional

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request, Query

from ..services.site_service import SiteService

from ...dependencies.templates import get_templates
from ...dependencies.services import get_site_service


__all__ = ['router']

router = APIRouter()


@router.get("/", include_in_schema=False)
async def _root(
        request: Request,
        sessionId: Annotated[Optional[str], Query(description="Идентификатор сессия для статистики и пользовательских взаимодействий на сайте")] = None,
        service: SiteService = Depends(get_site_service)
):
    likes_offset = None
    try: likes_offset = int(request.query_params.get('likes-offset'))
    except (ValueError, TypeError): pass

    session_id = sessionId or request.cookies.get('session_id')
    request.state.session_id = session_id

    template_params = await service.get_root(
        session_id,
        likes_offset,
        request.query_params.get('likes-sort')
    )

    templates = get_templates()
    response = templates.TemplateResponse(
        request=request,
        status_code=template_params.status_code,
        name=template_params.name,
        context=template_params.context
    )

    response.set_cookie('session_id', session_id, max_age=30 * 24 * 60 * 60, secure=True, httponly=True)
    if template_params.cookies:
        response.set_cookie(**template_params.cookies)

    return response


@router.head("/", include_in_schema=False)
async def _head_root():
    return HTMLResponse()
