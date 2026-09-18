from typing import Callable

from src.config.database.db_helper import db_helper
from ..repositories.tgbot_uow import TgBotUnitOfWork


__all__ = ['get_tgbot_uow_factory']


def get_tgbot_uow_factory() -> Callable[[], TgBotUnitOfWork]:
    """Зависимость для получения tgbot_uow_factory"""

    def app_uow_factory() -> TgBotUnitOfWork:
        return TgBotUnitOfWork(db_helper.session_factory)

    return app_uow_factory
