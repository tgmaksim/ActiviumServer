from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, WebAppInfo, KeyboardButton

from ...enums.emoji import EmojiIdList
from ...callbacks.menu import CallbackMenu
from ...callbacks.school_ea import CallbackSchoolEA


__all__ = ['menu_buttons', 'level_buttons', 'ea_buttons', 'delete_buttons', 'edit_ea_buttons']


def menu_buttons(list_ea_key: str, delete_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Список внеурочных занятий",
                callback_data=CallbackSchoolEA(action='list_ea', key=list_ea_key).pack(),
                icon_custom_emoji_id=EmojiIdList.school
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить все занятия",
                callback_data=CallbackSchoolEA(action='delete', key=delete_key).pack(),
                icon_custom_emoji_id=EmojiIdList.cross
            )
        ],
        [
            InlineKeyboardButton(
                text="Добавить внеурочные занятия",
                callback_data=CallbackSchoolEA(action='add').pack(),
                icon_custom_emoji_id=EmojiIdList.plus
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


def level_buttons(buttons_params: list[tuple[str, str]], nav_keys: list[str], nav_active: list[bool], delete_key: Optional[str], back_params: tuple[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        *([
            InlineKeyboardButton(
                text=text,
                callback_data=CallbackSchoolEA(action='list_ea', key=key).pack()
            )
        ] for text, key in buttons_params),
        [
            InlineKeyboardButton(
                text=" ",
                callback_data=CallbackSchoolEA(action='list_ea', key=nav_keys[0]).pack(),
                icon_custom_emoji_id=EmojiIdList.left if nav_active[0] else None
            ),
            InlineKeyboardButton(
                text=" ",
                callback_data=CallbackSchoolEA(action='list_ea', key=nav_keys[1]).pack(),
                icon_custom_emoji_id=EmojiIdList.update
            ),
            InlineKeyboardButton(
                text=" ",
                callback_data=CallbackSchoolEA(action='list_ea', key=nav_keys[2]).pack(),
                icon_custom_emoji_id=EmojiIdList.right if nav_active[2] else None
            )
        ],
        *([
            InlineKeyboardButton(
                text="Удалить все",
                callback_data=CallbackSchoolEA(action='delete', key=delete_key).pack(),
                icon_custom_emoji_id=EmojiIdList.cross
            )
        ] if delete_key else [],),
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackSchoolEA(action=back_params[0], key=back_params[1]).pack(),
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ])


def ea_buttons(edit_key: str, delete_key: str, back_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Изменить данные",
                callback_data=CallbackSchoolEA(action='edit', key=edit_key).pack(),
                icon_custom_emoji_id=EmojiIdList.pencil
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить внеурочное занятие",
                callback_data=CallbackSchoolEA(action='delete', key=delete_key).pack(),
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackSchoolEA(action='list_ea', key=back_key).pack(),
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ])


def delete_buttons(delete_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Да, удалить",
                callback_data=CallbackSchoolEA(action='confirm_delete', key=delete_key).pack(),
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackSchoolEA(action='menu').pack(),
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ])


def edit_ea_buttons(url: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text="Изменить внеурочное занятие",
                web_app=WebAppInfo(url=url)
            )
        ],
        [
            KeyboardButton(
                text="Отмена"
            )
        ]
    ], resize_keyboard=True)
