import locale
import asyncio

from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.project_config import settings  # Сначала project_config для загрузки env
from src.config.database.db_helper import db_helper

from background import add_backgrounds
from src.config.openapi import setup_openapi
from src.dependencies.httpx import get_httpx_client
from src.middlewares import setup_exception_handlers
from src.routers import get_api_router, get_site_router, get_public_api_router

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator:
    tasks = []
    get_httpx_client()

    try:
        tasks = add_backgrounds(asyncio.get_running_loop())

        service = LogService(get_log_uow_factory())
        await service.log(path='lifespan', value="Сервер запущен")

        yield  # Работа сервера

    finally:  # Завершение работы
        print("Сервер остановлен")

        service = LogService(get_log_uow_factory())
        await service.log(path='lifespan', value="Сервер остановлен")

        for task in tasks:
            task.cancel()

        await get_httpx_client().aclose()
        await db_helper.dispose()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        lifespan=lifespan,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # Скрытие сущностей в документации
    )

    setup_openapi(application, settings.HIDE_VALIDATION_ERRORS_IN_DOCS)
    setup_exception_handlers(application)

    application.include_router(get_site_router())
    application.include_router(get_api_router())
    application.include_router(get_public_api_router())
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = get_application()

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для работы datetime
