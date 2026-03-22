from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config.project_config import settings
from ..dependencies.templates import get_templates

from ..schemas.error_schema import ApiError
from ..schemas.response_schema import ApiResponse


__all__ = ['StableMiddleware']


class StableMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception:
            if request.url.path.startswith(settings.API_PREFIX):
                return JSONResponse(ApiResponse(
                    status=False,
                    error=ApiError(
                        type="InternalServerError"
                    )
                ).model_dump(by_alias=True), status_code=500)

            templates = get_templates()
            return templates.TemplateResponse(
                request=request,
                name="error.html",
                status_code=500,
                context={
                    "title": "Произошла ошибка на сервере",
                    "description": "При открытии страницы сервер получил непредвиденную ошибку"
                }
            )
