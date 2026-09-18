from dataclasses import dataclass, field

from typing import Union, Optional, Mapping

from aiogram.utils.formatting import Text
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, LinkPreviewOptions


__all__ = ['ServiceResult', 'ServiceParams']


class ServiceParams:
    def __init__(self, delete_keyboard: bool = False, delete_message: bool = False):
        self.delete_keyboard = delete_keyboard
        self.delete_message = delete_message


@dataclass()
class ServiceResult(Mapping):
    success: bool = True
    text: Optional[Union[str, Text]] = None
    alert: Optional[str] = None
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None
    link_preview_options: Optional[LinkPreviewOptions] = None

    service_params: ServiceParams = field(default_factory=ServiceParams)

    def _dict(self) -> dict[str, ...]:
        result = self.__dict__.copy()

        if isinstance(result['text'], Text):
            result.update(**result['text'].as_kwargs())

        result.pop('success')
        result.pop('alert')
        result.pop('service_params')

        return result

    # Для распаковки **
    def __iter__(self):
        return iter(self._dict())

    def __len__(self):
        return len(self._dict())

    def __getitem__(self, item: str):
        return self._dict().__getitem__(item)

    def keys(self) -> list[str]:
        return list(self._dict())
