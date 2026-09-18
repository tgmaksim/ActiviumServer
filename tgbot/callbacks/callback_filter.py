from typing import Literal, Any, Union, Optional

from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackQueryFilter as _CallbackQueryFilter, CallbackData

from ..dependencies.uow import get_tgbot_uow_factory


__all__ = ['CallbackQueryFilter']


class CallbackQueryFilter(_CallbackQueryFilter):
    async def __call__(self, query: CallbackQuery) -> Union[Literal[False], dict[str, Any]]:
        result = await super().__call__(query)

        if result is False:
            return result

        callback_data: CallbackData = result['callback_data']

        key: Optional[str]

        if (key := getattr(callback_data, 'key', None)) is not None:
            module = callback_data.__prefix__
            action = callback_data.action

            uow_factory = get_tgbot_uow_factory()
            async with uow_factory() as uow:
                data = await uow.tgbot_callback_data_repository.get_data(module, action, int(key))

            if data is None:
                return False

            result.update(params=data.data)

        return result
