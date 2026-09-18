from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .tgbot_state_repository import TgbotStateRepository
from .tgbot_callback_data_repository import TgbotCallbackDataRepository

from src.repositories.sqlalchemy_uow import SqlAlchemyUnitOfWork


__all__ = ['TgBotUnitOfWork']


class TgBotUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory)

        self._tgbot_state_repository: Optional[TgbotStateRepository] = None
        self._tgbot_callback_data_repository: Optional[TgbotCallbackDataRepository] = None

    @property
    def tgbot_state_repository(self) -> TgbotStateRepository:
        if self._tgbot_state_repository is None:
            self._tgbot_state_repository = TgbotStateRepository(self.queue)
        return self._tgbot_state_repository

    @property
    def tgbot_callback_data_repository(self) -> TgbotCallbackDataRepository:
        if self._tgbot_callback_data_repository is None:
            self._tgbot_callback_data_repository = TgbotCallbackDataRepository(self.queue)
        return self._tgbot_callback_data_repository
