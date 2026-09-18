from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.callbacks.school_ea import CallbackSchoolEA
from tgbot.callbacks.school_bells import CallbackSchoolBells
from tgbot.callbacks.school_posts import CallbackSchoolPosts
from tgbot.callbacks.school_stats import CallbackSchoolStats
from tgbot.callbacks.school_admins import CallbackSchoolAdmins

from tgbot.enums.emoji import EmojiIdList


__all__ = ['menu_buttons']


def menu_buttons() -> InlineKeyboardMarkup:
    """Кнопки главного меню администратора образовательной организации"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Звонки",
                icon_custom_emoji_id=EmojiIdList.bell,
                callback_data=CallbackSchoolBells().pack()
            ),
            InlineKeyboardButton(
                text="Статистика",
                icon_custom_emoji_id=EmojiIdList.histogram,
                callback_data=CallbackSchoolStats().pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Внеурочные занятия",
                icon_custom_emoji_id=EmojiIdList.school,
                callback_data=CallbackSchoolEA().pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Новости и мероприятия",
                icon_custom_emoji_id=EmojiIdList.microphone,
                callback_data=CallbackSchoolPosts().pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Мои администраторы",
                icon_custom_emoji_id=EmojiIdList.verified,
                callback_data=CallbackSchoolAdmins().pack()
            )
        ]
    ])
