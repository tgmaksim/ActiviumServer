import locale
import asyncio

from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config.project_config import settings
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
    get_httpx_client()  # Инициализация httpx-клиента

    try:
        # Запуск фоновых задач
        tasks = add_backgrounds(
            asyncio.get_running_loop(),
            tgbot=settings.START_TGBOT_WORKER,
            marks_notifications=settings.START_MARKS_NOTIFICATIONS_WORKER,
            ea_notifications=settings.START_EA_NOTIFICATIONS_WORKER,
            notes_notifications=settings.START_NOTES_NOTIFICATIONS_WORKER
        )

        service = LogService(get_log_uow_factory())
        await service.log(path='lifespan', value="Сервер запущен")

        yield  # Работа сервера

    finally:  # Завершение работы
        print("Сервер остановлен")

        service = LogService(get_log_uow_factory())
        await service.log(path='lifespan', value="Сервер остановлен")

        for task in tasks:
            task.cancel()  # Завершение запущенных фоновых процессов

        # Закрытие соединений
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

    # Для отладочного запуска статические файлы отправляются через fastapi
    # В product-запуске статические файлы передаются nginx
    if settings.DEBUG:
        application.mount('/', StaticFiles(directory=settings.WWW_PATH), name='static')

    if not settings.DEBUG:
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
