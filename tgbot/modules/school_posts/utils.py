from aiogram.types import Message
from aiogram.utils.formatting import Text

from ...enums.emoji import EmojiList


__all__ = ['send_loading']


async def send_loading(message: Message, text: str):
    """Отправка сообщения с эмодзи загрузки"""

    text = Text(
        text, " ", EmojiList.loading.value
    )

    return await message.answer(**text.as_kwargs())
