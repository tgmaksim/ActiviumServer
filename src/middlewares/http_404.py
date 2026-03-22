from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from ..schemas.error_schema import ApiError
from ..schemas.response_schema import ApiResponse
from ..dependencies.templates import get_templates

from ..config.project_config import settings


__all__ = ['http_404_handler']


async def http_404_handler(request: Request, exc: HTTPException) -> Response:
    request.state.error = str(exc)

    if request.url.path.startswith(settings.API_PREFIX):
        return JSONResponse(ApiResponse(
            status=False,
            error=ApiError(
                type="ApiMethodNotFoundError",
                errorMessage="Метод не существует"
            )
        ).model_dump(by_alias=True), status_code=404)

    if request.url.path.startswith(settings.APK_PREFIX):
        description = "Файл с обновлением не найден. Попробуйте позже или обратитесь в поддержку"
    else:
        description = "Страница, которую Вы пытались получить не найдена, или, возможно, перемещена"

    templates = get_templates()
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        status_code=404,
        context={
            "title": "Страница не найдена",
            "description": description
        }
    )
