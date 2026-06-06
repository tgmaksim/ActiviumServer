from dataclasses import dataclass

from typing import Union, Optional, Mapping

from aiogram.utils.formatting import Text
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, LinkPreviewOptions


__all__ = ['MessageModel']


@dataclass()
class MessageModel(Mapping):
    text: Union[str, Text]
    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None
    link_preview_options: Optional[LinkPreviewOptions] = None

    def _dict(self) -> dict[str, ...]:
        result = self.__dict__
        if isinstance(result['text'], Text):
            result.update(**result['text'].as_kwargs())

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
