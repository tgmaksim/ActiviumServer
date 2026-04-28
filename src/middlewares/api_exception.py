import traceback

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from ..api.api_key_error import ApiKeyError
from ..api.session_error import SessionError
from ..dependencies.uow import get_app_uow_factory
from ..api.base_api_exception import BaseApiException

from ..schemas.error_schema import ApiError
from ..schemas.response_schema import ApiResponse


__all__ = ['api_exception_handler']


async def api_exception_handler(request: Request, exc: BaseApiException) -> Response:
    """Обработчик API-ошибок базового класса BaseApiException"""

    if isinstance(exc, ApiKeyError):
        request.state.error = '\n'.join(traceback.format_exception(exc))  # Для логирования ошибки

        return JSONResponse(ApiResponse(
            status=False,
            error=ApiError(
                type="ApiKeyError",
                errorMessage="Данное приложение не имеет прав на получение данных"
            )
        ).model_dump(by_alias=True), status_code=403)

    elif isinstance(exc, SessionError):
        request.state.error = '\n'.join(traceback.format_exception(exc))  # Для логирования ошибки

        async with get_app_uow_factory()() as uow:
            await uow.session_repository.kill_session(exc.session_id)  # life=false

        return JSONResponse(ApiResponse(
            status=False,
            error=ApiError(
                type="UnauthorizedError",
                errorMessage="Требуется повторная авторизация"
            )
        ).model_dump(by_alias=True), status_code=403)

    raise exc from exc  # Продвижение ошибки до middleware
