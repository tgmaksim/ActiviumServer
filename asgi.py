from fastapi.requests import Request
from fastapi.applications import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core import log, templates

from api.entities import ApiResponse, ApiError
from api.status.entities import VersionsResult
from api.middleware import ExceptionHandlerMiddleware
from api.status.functions import get_latest_version, get_previous_versions

from api.login import router as login
from api.status import router as status
from api.dnevnik import router as dnevnik


app = FastAPI()
app.add_middleware(ExceptionHandlerMiddleware)

app.include_router(status)
app.include_router(login)
app.include_router(dnevnik)


# Статические файлы находятся в папке www и передаются низкоуровневым сервером
@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False  # Не отображается в документации
)
async def _root(request: Request):
    session = request.cookies.get("session")

    try:
        versions = await get_latest_version()
        previous_versions = await get_previous_versions()

    except Exception as e:
        await log(request, request.url.path, session, f"{e.__class__.__name__}: {e}")
        versions = VersionsResult(
            latestVersionNumber=0,
            latestVersionString="0.0.0",
            date="",
            versionStatus="Новая версия",
            updateLogs="Исправлены ошибки"
        )  # Значения по умолчанию
        previous_versions = []
    else:
        await log(request, request.url.path, session, "200 OK")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "version": versions.latestVersionString,
            "date": versions.date,
            "version_status": versions.versionStatus,
            "update_log": versions.updateLogs.split('\n'),
            "previous_versions": [{
                "version": version.latestVersionString,
                "date": version.date,
                "versionStatus": version.versionStatus,
                "version_status": version.versionStatus,
                "update_log": version.updateLogs.split('\n'),
            } for version in previous_versions if version.latestVersionNumber != versions.latestVersionNumber]
        }
    )


# Глобальный обработчик ошибок RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, __: RequestValidationError):
    return JSONResponse(ApiResponse(
        status=False,
        error=ApiError(
            type="ValidationError"
        )
    ).model_dump())


# Глобальный обработчик HTTP-ошибок
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(ApiResponse(
            status=False,
            error=ApiError(
                type="ApiMethodNotFoundError"
            )
        ).model_dump())

    return JSONResponse(ApiResponse(
        status=False,
        error=ApiError(
            type="InternalServerError"
        )
    ).model_dump())


# Некоторые изменения в документации
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    app.openapi_schema = get_openapi(
        title="API приложения Гимназия №147",
        summary="Подробное руководство по структуре API приложения Гимназия №147",
        description="Данная документация представляет полную информацию по работе с API. Ключевой особенностью "
                    "является идентификатор (classId) каждой сущности: как входной, так и результативной. Он позволяет "
                    "разным версиям приложения использовать API должным образом, даже если определенный метод изменил "
                    "структуру входных/выходных данных или больше не поддерживается. В каталоге сущностей можно найти "
                    "все идентификаторы",
        contact={"Максим Дрючин": "@tgmaksim_company"},
        version="1.0",
        routes=app.routes
    )

    for _, method_item in app.openapi_schema.get('paths').items():
        for _, param in method_item.items():
            responses = param.get('responses')
            if '422' in responses:
                del responses['422']  # Удаление информации об ошибке RequestValidationError в документации

    schemas = app.openapi_schema.get('components', {}).get('schemas', {})

    if 'HTTPValidationError' in schemas:
        del schemas['HTTPValidationError']  # Удаление информации об ошибке HTTPValidationError в документации
    if 'ValidationError' in schemas:
        del schemas['ValidationError']  # Удаление информации об ошибке ValidationError в документации

    return app.openapi_schema


app.openapi = custom_openapi
