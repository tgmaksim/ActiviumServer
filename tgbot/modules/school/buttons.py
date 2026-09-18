from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton

from ...enums.emoji import EmojiIdList


__all__ = ['school_links']


def school_links(login_url: str, share_url: str) -> InlineKeyboardMarkup:
    """Кнопки со ссылками для различных способов авторизации администратора образовательной организации"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Войти в Дневник.ру",
                url=login_url,
                icon_custom_emoji_id=EmojiIdList.dnevnikru
            )
        ],
        [
            InlineKeyboardButton(
                text="Попросить другого",
                url=share_url,
                icon_custom_emoji_id=EmojiIdList.share
            )
        ],
        [
            InlineKeyboardButton(
                text="Скопировать ссылку",
                copy_text=CopyTextButton(text=login_url)
            )
        ]
    ])
