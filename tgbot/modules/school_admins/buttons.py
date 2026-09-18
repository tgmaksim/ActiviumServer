from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButtonRequestUsers
)

from ...enums.emoji import EmojiIdList
from ...callbacks.menu import CallbackMenu
from ...callbacks.school_admins import CallbackSchoolAdmins


__all__ = ['my_admins_buttons', 'add_admin_buttons']


def my_admins_buttons(my_admins: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    """Кнопки для удаления и добавления администраторов образовательной организации"""

    return InlineKeyboardMarkup(inline_keyboard=[
        *([
            InlineKeyboardButton(
                text=admin_name,
                callback_data=CallbackSchoolAdmins(action='delete', user_id=admin_id).pack(),
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ] for admin_id, admin_name in my_admins),
        [
            InlineKeyboardButton(
                text="Добавить администратора",
                callback_data=CallbackSchoolAdmins(action='add').pack(),
                icon_custom_emoji_id=EmojiIdList.plus
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackMenu().pack(),
                icon_custom_emoji_id=EmojiIdList.back,
            )
        ]
    ])


def add_admin_buttons() -> ReplyKeyboardMarkup:
    """Клавиатурные кнопки для добавления администраторов образовательной организации"""

    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text="Выбрать пользователя(ей)",
                request_users=KeyboardButtonRequestUsers(
                    request_id=1,
                    user_is_bot=False,
                    request_name=True,
                    max_quantity=10
                )
            )
        ],
        [
            KeyboardButton(
                text="Отмена",
                icon_custom_emoji_id=EmojiIdList.cross
            )
        ]
    ], is_persistent=True, resize_keyboard=True, input_field_placeholder="Выберите кнопкой")
