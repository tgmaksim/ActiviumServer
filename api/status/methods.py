from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from core import log

from api.entities import ApiError
from api.core import check_api_key

from . functions import get_latest_version
from . entities import VersionsApiRequest, VersionsResult, VersionsApiResponse


router = APIRouter(prefix=f"/status", tags=["Status"])
__all__ = ['router']


@router.post(
    f"/checkVersion/{VersionsApiRequest.classId}",
    summary="Проверка версии приложения",
    description="Получение информации о последней версии приложения и обновлении",
    response_model=VersionsApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def _check_version(request: Request, request_data: VersionsApiRequest):
    if not await check_api_key(request_data.apiKey):
        return VersionsApiResponse(
            status=False,
            error=ApiError(
                type="InvalidApiKeyError",
                errorMessage="Приложение повреждено или скачано из неофициального источника. Обратитесь в поддержку"
            )
        )

    try:
        versions: VersionsResult = await get_latest_version()

    except Exception as e:
        await log(request, request.base_url.path, None, f"{e.__class__.__name__}: {e}")
        return VersionsApiResponse(
            status=False,
            error=ApiError(
                type="InternalServerError"
            )
        )
    else:
        await log(request, request.base_url.path, None, "200 OK")
        return VersionsApiResponse(answer=versions)
