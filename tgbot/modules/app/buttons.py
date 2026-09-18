from ...enums.emoji import EmojiIdList
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.config.project_config import settings


__all__ = ['resources_buttons']


def resources_buttons() -> InlineKeyboardMarkup:
    """Кнопки со ссылками на ресурсы приложения"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скачать", icon_custom_emoji_id=EmojiIdList.android, url=settings.URL_FOR_TG)],
        [InlineKeyboardButton(text="Исходный код", icon_custom_emoji_id=EmojiIdList.github, url=settings.GITHUB)]
    ])
