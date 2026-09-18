from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ...enums.emoji import EmojiIdList
from ...callbacks.menu import CallbackMenu
from ...callbacks.school_stats import CallbackSchoolStats


__all__ = ['menu_buttons', 'back_button']


def menu_buttons() -> InlineKeyboardMarkup:
    """Меню статистики образовательной организации"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Сформировать отчет",
                callback_data=CallbackSchoolStats(action='create').pack(),
                icon_custom_emoji_id=EmojiIdList.pie_chart
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackMenu().pack(),
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ])


def back_button() -> InlineKeyboardMarkup:
    """Кнопка Назад"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackMenu().pack(),
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ])
