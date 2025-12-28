import traceback

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core import log
from . core import ApiKeyError, SessionError
from . entities import ApiResponse, ApiError


__all__ = ['ExceptionHandlerMiddleware']


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ApiKeyError as e:
            await log(request, request.url.path, None, f"ApiKeyError(api_key={e.api_key})")
            return JSONResponse(ApiResponse(
                status=False,
                error=ApiError(
                    type="InvalidApiKeyError",
                    errorMessage="Приложение повреждено или скачано из неофициального источника. Обратитесь в поддержку"
                )
            ).model_dump(by_alias=True))
        except SessionError as e:
            await log(request, request.url.path, e.session, "Unauthorized")
            return JSONResponse(ApiResponse(
                status=False,
                error=ApiError(
                    type="UnauthorizedError",
                    errorMessage="Требуется повторная авторизация"
                )
            ).model_dump(by_alias=True))
        except Exception as e:
            await log(request, request.url.path, None, f"{e.__class__.__name__}: {e}")
            print(''.join(traceback.format_exception(e)))
            return JSONResponse(ApiResponse(
                status=False,
                error=ApiError(
                    type="InternalServerError",
                    errorMessage=None
                )
            ).model_dump(by_alias=True))
