from typing import Optional, Any

from ...repositories.db_queue import AsyncDBQueue
from ...models.tgbot_state_model import TgbotState

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['TgbotStateRepository']


class TgbotStateRepository(SqlAlchemyRepository[TgbotState]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, TgbotState)

    async def get_state(self, key: str) -> Optional[TgbotState]:
        return await self.get_single(TgbotState.key == key)

    async def set_state(self, key: str, state: Optional[str]) -> Optional[TgbotState]:
        return await self.create({
            'key': key,
            'state': state
        }, security=['key'])

    async def set_data(self, key: str, data: Optional[dict[str, Any]]) -> Optional[TgbotState]:
        return await self.create({
            'key': key,
            'data': data
        }, security=['key'])
