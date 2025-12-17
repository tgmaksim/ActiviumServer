import traceback

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from . entities import ApiResponse, ApiError


__all__ = ['ExceptionHandlerMiddleware']


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except Exception as e:
            print(''.join(traceback.format_exception(e)))
            return JSONResponse(ApiResponse(
                status=False,
                error=ApiError(
                    type="InternalServerError",
                    errorMessage=None
                )
            ).model_dump())
