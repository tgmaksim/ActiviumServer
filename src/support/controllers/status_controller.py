from typing import Annotated, Optional

from fastapi import APIRouter, Query, Depends

from ..schemas.status_schemas import VersionsApiResponse, HealthApiResponse

from ..services.status_service import StatusService
from ...dependencies.services import get_status_service


__all__ = ['router']

router = APIRouter(prefix='/status', tags=["Status"])


@router.get(
    "/checkVersion/0",
    summary="Проверка версии приложения",
    description="Получение информации о последней версии приложения и обновлении",
    response_model=VersionsApiResponse
)
async def _checkVersion0(
        versionNumber: Annotated[Optional[int], Query(description="Текущая версия (номер сборки) приложения")] = None,
        service: StatusService = Depends(get_status_service)
) -> VersionsApiResponse:
    return await service.check_latest_version(versionNumber)


@router.get(
    "/health/0",
    summary="Проверка работоспособности сервера",
    response_model=HealthApiResponse
)
async def _health0(service: StatusService = Depends(get_status_service)) -> HealthApiResponse:
    return await service.health()
