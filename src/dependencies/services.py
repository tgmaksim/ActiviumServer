from typing import Callable

from fastapi import Depends
from httpx import AsyncClient

from .httpx import get_httpx_client
from .uow import get_app_uow_factory

from ..support.repositories.app_uow import AppUnitOfWork

from ..support.services.site_service import SiteService
from ..support.services.login_service import LoginService
from ..support.services.status_service import StatusService
from ..support.services.school_service import SchoolService
from ..support.services.dnevnik_service import DnevnikService
from ..support.services.reviews_service import ReviewsService
from ..support.services.settings_service import SettingsService
from ..support.services.dnevnik_tools_service import DnevnikToolsService


__all__ = ['get_status_service', 'get_site_service', 'get_login_service', 'get_dnevnik_service', 'get_settings_service',
           'get_reviews_service', 'get_dnevnik_tools_service', 'get_school_service']


def get_status_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory)
) -> StatusService:
    """Зависимость FastApi для получения StatusService"""

    return StatusService(uow_factory)


def get_site_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory)
) -> SiteService:
    """Зависимость FastApi для получения SiteService"""

    return SiteService(uow_factory)


def get_login_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory),
        httpx_client: AsyncClient = Depends(get_httpx_client)
) -> LoginService:
    """Зависимость FastApi для получения LoginService"""

    return LoginService(uow_factory, httpx_client)


def get_dnevnik_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory),
        httpx_client: AsyncClient = Depends(get_httpx_client)
) -> DnevnikService:
    """Зависимость FastApi для получения DnevnikService"""

    return DnevnikService(uow_factory, httpx_client)


def get_settings_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory),
        httpx_client: AsyncClient = Depends(get_httpx_client)
) -> SettingsService:
    """Зависимость FastApi для получения SettingsService"""

    return SettingsService(uow_factory, httpx_client)


def get_reviews_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory),
        httpx_client: AsyncClient = Depends(get_httpx_client)
) -> ReviewsService:
    """Зависимость FastApi для получения ReviewsService"""

    return ReviewsService(uow_factory, httpx_client)


def get_dnevnik_tools_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory),
        httpx_client: AsyncClient = Depends(get_httpx_client)
) -> DnevnikToolsService:
    """Зависимость FastApi для получения DnevnikToolsService"""

    return DnevnikToolsService(uow_factory, httpx_client)

def get_school_service(
        uow_factory: Callable[[], AppUnitOfWork] = Depends(get_app_uow_factory),
        httpx_client: AsyncClient = Depends(get_httpx_client)
) -> SchoolService:
    """Зависимость FastApi для получения SchoolService"""

    return SchoolService(uow_factory, httpx_client)
