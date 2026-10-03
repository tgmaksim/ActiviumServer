from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request

from ..services.web_app_service import WebAppService

from ...dependencies.services import get_web_app_service


__all__ = ['public_router']

public_router = APIRouter(prefix="/app", tags=["WebApp"], include_in_schema=False)
"""Публичный router Web-приложения"""


@public_router.get("")
async def _app(
        request: Request,
        service: WebAppService = Depends(get_web_app_service)
) -> HTMLResponse:
    template_params = service.app()

    return template_params.to_response(request)


@public_router.get("/login")
async def _app(
        request: Request,
        service: WebAppService = Depends(get_web_app_service)
) -> HTMLResponse:
    template_params = service.login()

    return template_params.to_response(request)