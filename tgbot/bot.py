from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from .config import settings
from .routers import get_tg_router


__all__ = ['create_bot_and_dispatcher', 'get_bot']


_bot: Optional[Bot] = None
_dp: Optional[Dispatcher] = None


def get_bot() -> Bot:
    global _bot, _dp
    if not _bot:
        create_bot_and_dispatcher()

    return _bot


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    from .middlewares.logging import LoggingMiddleware  # fix circular import
    dp.update.outer_middleware(LoggingMiddleware())

    dp.include_router(get_tg_router())

    global _bot, _dp
    _bot, _dp = bot, dp

    return bot, dp
