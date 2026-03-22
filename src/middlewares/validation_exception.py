from fastapi import Request, Response
from fastapi.responses import JSONResponse

from fastapi.exceptions import RequestValidationError

from ..schemas.error_schema import ApiError
from ..schemas.response_schema import ApiResponse


__all__ = ['validation_exception_handler']


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    request.state.error = f"{exc.__class__.__name__}: {exc}"

    return JSONResponse(ApiResponse(
        status=False,
        error=ApiError(
            type="ValidationError",
            errorMessage="Приложение отправило некорректные данные"
        )
    ).model_dump(by_alias=True), status_code=422)
