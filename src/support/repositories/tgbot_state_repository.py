from typing import Optional, Any

from ...repositories.db_queue import AsyncDBQueue
from ...models.tgbot_state_model import TgbotState

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['TgbotStateRepository']


class TgbotStateRepository(SqlAlchemyRepository[TgbotState]):
    """Репозиторий для хранения состояний пользователей в чате с Telegram-ботов"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, TgbotState)

    async def get_state(self, key: str) -> Optional[TgbotState]:
        """
        Получить состояние пользователя в чате

        :param key: идентификатор пользователя и чата
        :return: состояние пользователя в чате, если существует
        """

        return await self.get_single(TgbotState.key == key)

    async def set_state(self, key: str, state: Optional[str]) -> TgbotState:
        """
        Изменить состояние пользователя в чате

        :param key: идентификатор пользователя и чата
        :param state: новое состояние пользователя
        :return: обновленное состояние
        """

        return await self.create({
            'key': key,
            'state': state
        }, security=['key'])

    async def set_data(self, key: str, data: Optional[dict[str, Any]]) -> TgbotState:
        """
        Изменить дополнительные данные состояния пользователя в чате

        :param key: идентификатор пользователя и чата
        :param data: новые дополнительные данные состояния пользователя
        :return: обновленное состояние
        """

        return await self.create({
            'key': key,
            'data': data
        }, security=['key'])
