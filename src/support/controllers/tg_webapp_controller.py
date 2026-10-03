from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request

from ..services.tg_webapp_service import TgWebAppService

from ...dependencies.templates import get_templates
from ...dependencies.services import get_tg_webapp_service


__all__ = ['public_router']

public_router = APIRouter(prefix="/tg-webapp", tags=["Tg-WebApp"], include_in_schema=False)
"""Публичный router сайта"""


@public_router.get("/bells")
async def _bells(
        request: Request,
        service: TgWebAppService = Depends(get_tg_webapp_service)
) -> HTMLResponse:
    template_params = await service.bells()

    return template_params.to_response(request)


@public_router.get("/extracurricular_activity/edit")
async def _extracurricular_activity_edit(
        request: Request,
        service: TgWebAppService = Depends(get_tg_webapp_service)
) -> HTMLResponse:
    template_params = await service.extracurricular_activity_edit()

    return template_params.to_response(request)
