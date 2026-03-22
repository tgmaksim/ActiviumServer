from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request

from ..services.site_service import SiteService

from ...dependencies.templates import get_templates
from ...dependencies.services import get_site_service


__all__ = ['router']

router = APIRouter()


@router.get("/", include_in_schema=False)
async def _root(request: Request, service: SiteService = Depends(get_site_service)):
    likes_offset = None
    try: likes_offset = int(request.query_params.get('likes-offset'))
    except (ValueError, TypeError): pass

    template_params = await service.get_root(
        request.cookies.get('session_id'),
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

    if template_params.cookies:
        response.set_cookie(**template_params.cookies)

    return response


@router.head("/", include_in_schema=False)
async def _head_root():
    return HTMLResponse()
