from typing import Union

from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi.background import BackgroundTasks

from core import log
from api.core import assert_check_api_key

from . functions import get_latest_version
from . entities import (
    VersionsResult,
    VersionsApiRequest,
    VersionsApiResponse,
    VersionsApiRequest0x00000004,
)


__all__ = ['router']

router = APIRouter(prefix=f"/status", tags=["Status"])


@router.post(
    f"/checkVersion/{VersionsApiRequest0x00000004.classId}",
    summary="Проверка версии приложения",
    description=f"Получение информации о последней версии приложения и обновлении. "
                f"Устаревший в пользу {VersionsApiRequest.classId}",
    response_model=VersionsApiResponse,
    response_class=JSONResponse,
    status_code=200,
    deprecated=True
)
async def _checkVersion0x00000004(request: Request, request_data: VersionsApiRequest0x00000004, background_tasks: BackgroundTasks):
    return await checkVersionRequest(request, request_data, background_tasks)


@router.post(
    f"/checkVersion/{VersionsApiRequest.classId}",
    summary="Проверка версии приложения",
    description="Получение информации о последней версии приложения и обновлении. Статус новой версии рассчитывается, "
                "учитывая номер сборки приложения в входных данных",
    response_model=VersionsApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def _checkVersion(request: Request, request_data: VersionsApiRequest, background_tasks: BackgroundTasks):
    return await checkVersionRequest(request, request_data, background_tasks)


async def checkVersionRequest(request: Request, request_data: Union[VersionsApiRequest0x00000004, VersionsApiRequest], background_tasks: BackgroundTasks):
    await assert_check_api_key(request_data.apiKey)

    if request_data.classId == VersionsApiRequest.classId:
        versions: VersionsResult = await get_latest_version(request_data.data.versionNumber)
    else:
        versions: VersionsResult = await get_latest_version()

    background_tasks.add_task(log, request, request.url.path, None, "200 OK")
    return VersionsApiResponse(answer=versions)
