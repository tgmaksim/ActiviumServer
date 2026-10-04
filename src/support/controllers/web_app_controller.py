from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request

from ..schemas.web_app_schemas import LoginUrl
from ..services.web_app_service import WebAppService

from ...dependencies.services import get_web_app_service


__all__ = ['public_router']

public_router = APIRouter(prefix="/app", tags=["WebApp"])
"""Публичный router Web-приложения"""


@public_router.get("", include_in_schema=False)
async def _app(
        request: Request,
        service: WebAppService = Depends(get_web_app_service)
) -> HTMLResponse:
    template_params = service.app()

    return template_params.to_response(request)


@public_router.get("/login", include_in_schema=False)
async def _app(
        request: Request,
        service: WebAppService = Depends(get_web_app_service)
) -> HTMLResponse:
    template_params = service.app()

    return template_params.to_response(request)


@public_router.get("/loginUrl", include_in_schema=True)
async def _loginUrl(
        service: WebAppService = Depends(get_web_app_service)
) -> LoginUrl:
    return await service.login()
