from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request

from ..services.web_app_service import WebAppService

from ...dependencies.templates import get_templates
from ...dependencies.services import get_web_app_service


__all__ = ['public_router']

public_router = APIRouter(prefix="/app", tags=["WebApp"], include_in_schema=False)
"""Публичный router Web-приложения"""


@public_router.get("/")
async def _app(
        request: Request,
        service: WebAppService = Depends(get_web_app_service)
) -> HTMLResponse:
    template_params = service.app()

    templates = get_templates()
    response = templates.TemplateResponse(
        request=request,
        status_code=template_params.status_code,
        name=template_params.name,
        context=template_params.context
    )

    if template_params.cookies:
        for cookie in template_params.cookies:
            response.set_cookie(**cookie)

    return response