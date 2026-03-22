from fastapi import APIRouter, Depends

from .config.project_config import settings
from .dependencies.security import check_api_key

from .support.controllers import (
    site_controller,
    login_controller,
    status_controller,
    dnevnik_controller,
    reviews_controller,
    settings_controller,
    dnevnik_tools_controller
)

__all__ = ['get_api_router', 'get_site_router', 'get_public_api_router']


def get_api_router() -> APIRouter:
    router = APIRouter(dependencies=[Depends(check_api_key)], responses={
        500: {"description": "Внутренняя ошибка сервера при обработке запроса", "response_description": "Internal Server Error"},
        422: {"description": "Неверный формат входных данных", "response_description": "Unprocessable Entity"},
        404: {"description": "Запрашиваемый метод не найден", "response_description": "Not found"},
        403: {"description": "Нет прав для доступа к ресурсу(ам)", "response_description": "Forbidden"},
    })
    router.include_router(status_controller.router, prefix=settings.API_PREFIX)
    router.include_router(login_controller.router, prefix=settings.API_PREFIX)
    router.include_router(dnevnik_controller.router, prefix=settings.API_PREFIX)
    router.include_router(settings_controller.router, prefix=settings.API_PREFIX)
    router.include_router(reviews_controller.router, prefix=settings.API_PREFIX)
    router.include_router(dnevnik_tools_controller.router, prefix=settings.API_PREFIX)

    return router


def get_public_api_router() -> APIRouter:
    public_router = APIRouter(responses={
        500: {"description": "Внутренняя ошибка сервера", "response_description": "Internal Server Error"},
        404: {"description": "Запрашиваемый метод не найден", "response_description": "Not found"}
    })
    public_router.include_router(login_controller.public_router)
    public_router.include_router(reviews_controller.public_router)

    return public_router


def get_site_router() -> APIRouter:
    router = APIRouter()
    router.include_router(site_controller.router)
    return router
