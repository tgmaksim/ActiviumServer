from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ...enums.emoji import EmojiIdList
from ...callbacks.reviews import CallbackReviews


__all__ = ['admin_choice']


def admin_choice(parent_id: int) -> InlineKeyboardMarkup:
    """Кнопки для модерации отзывов"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Опубликовать",
                callback_data=CallbackReviews(publish=True, parent_id=parent_id).pack(),
                icon_custom_emoji_id=EmojiIdList.check_mark,
                style='success'
            )
        ],
        [
            InlineKeyboardButton(
                text="Уведомить о нарушении",
                callback_data=CallbackReviews(publish=False, parent_id=parent_id).pack(),
                icon_custom_emoji_id=EmojiIdList.warning_red,
                style='danger'
            )
        ]
    ])
