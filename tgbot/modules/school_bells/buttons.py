from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from ...enums.emoji import EmojiIdList
from ...callbacks.menu import CallbackMenu
from ...callbacks.school_bells import CallbackSchoolBells


__all__ = ['bells_buttons', 'bell_buttons', 'create_or_edit_buttons']


def bells_buttons(bells: list[tuple[int, str, str]]) -> InlineKeyboardMarkup:
    """Список звонковых расписаний и кнопка для добавления"""

    return InlineKeyboardMarkup(inline_keyboard=[
        *([
            InlineKeyboardButton(
                text=f"На {weekdays} за {months}",
                callback_data=CallbackSchoolBells(action='item', hour_id=hour_id).pack()
            )
        ] for hour_id, months, weekdays in bells),
        [
            InlineKeyboardButton(
                text="Добавить расписание",
                callback_data=CallbackSchoolBells(action='add').pack(),
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


def bell_buttons(hour_id: int) -> InlineKeyboardMarkup:
    """Меню звонкового расписания"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Редактировать расписание",
                callback_data=CallbackSchoolBells(action='edit', hour_id=hour_id).pack(),
                icon_custom_emoji_id=EmojiIdList.pencil
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить расписание",
                callback_data=CallbackSchoolBells(action='delete', hour_id=hour_id).pack(),
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackSchoolBells(action='menu').pack(),
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ])


def create_or_edit_buttons(url: str) -> ReplyKeyboardMarkup:
    """Клавиатурные кнопки для добавления или редактирования звонкового расписания"""

    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text="Открыть редактор расписания",
                web_app=WebAppInfo(url=url)
            )
        ],
        [
            KeyboardButton(
                text="Отмена",
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ], resize_keyboard=True)
