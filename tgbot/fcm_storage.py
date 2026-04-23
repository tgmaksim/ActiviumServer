from typing import Any, Dict, Optional, Callable

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType, KeyBuilder, DefaultKeyBuilder

from src.support.repositories.app_uow import AppUnitOfWork


class PostgresStorage(BaseStorage):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], key_builder: KeyBuilder | None = None,):
        self.uow_factory = uow_factory
        self._key_builder = key_builder or DefaultKeyBuilder()

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        async with self.uow_factory() as uow:
            await uow.tgbot_state_repository.set_state(
                self._key_builder.build(key),
                state.state if isinstance(state, State) else state
            )

    async def get_state(self, key: StorageKey) -> Optional[str]:
        async with self.uow_factory() as uow:
            state = await uow.tgbot_state_repository.get_state(self._key_builder.build(key))
            return state.state if state else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        async with self.uow_factory() as uow:
            await uow.tgbot_state_repository.set_data(self._key_builder.build(key), data)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        async with self.uow_factory() as uow:
            state = await uow.tgbot_state_repository.get_state(self._key_builder.build(key))
            return state.data.copy() if state else {}

    async def close(self) -> None:
        pass
