from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import SimpleEventIsolation

from src.config.project_config import settings


__all__ = ['create_bot_and_dispatcher', 'get_bot']

# Экземпляры бота и диспетчера
_bot: Optional[Bot] = None
_dp: Optional[Dispatcher] = None


def get_bot() -> Bot:
    """Получить экземпляр бота"""

    global _bot, _dp
    if not _bot:
        create_bot_and_dispatcher()

    return _bot


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Создать и настроить экземпляры Telegram-бота и его диспетчера"""

    from ..routers import get_tg_router
    from .fcm_storage import PostgresStorage

    from ..middlewares.logging import LoggingMiddleware
    from ..middlewares.api_exception import ApiMiddleware

    from src.dependencies.uow import get_app_uow_factory

    # По умолчанию все сообщения будут отправляться с parse_mode=html
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Используется та же БД на Postgres для хранения состояний пользователей
    storage = PostgresStorage(get_app_uow_factory())
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())

    dp.update.outer_middleware(ApiMiddleware())
    dp.update.outer_middleware(LoggingMiddleware())

    dp.include_router(get_tg_router())

    # Сохранение экземпляра бота и диспетчера
    global _bot, _dp
    _bot, _dp = bot, dp

    return bot, dp
