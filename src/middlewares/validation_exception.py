import traceback

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from fastapi.exceptions import RequestValidationError

from ..schemas.error_schema import ApiError
from ..schemas.response_schema import ApiResponse


__all__ = ['validation_exception_handler']


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    """Обработчик ошибки RequestValidationError для возвращения корректного API-ответа"""

    request.state.error = '\n'.join(traceback.format_exception(exc))  # Для логирования ошибки

    return JSONResponse(ApiResponse(
        status=False,
        error=ApiError(
            type="ValidationError",
            errorMessage="Приложение отправило некорректные данные"
        )
    ).model_dump(by_alias=True), status_code=422)
