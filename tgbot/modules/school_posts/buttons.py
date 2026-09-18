from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from ...enums.emoji import EmojiIdList
from ...callbacks.menu import CallbackMenu
from ...callbacks.school_posts import CallbackSchoolPosts


__all__ = ['posts_buttons', 'post_buttons', 'back_button', 'optional_stage_buttons', 'stage_buttons', 'stage_content_buttons']


def posts_buttons(posts: list[tuple[int, str]], offset: int, left_offset: int, right_offset: int) -> InlineKeyboardMarkup:
    """Навигационное меню с постами и кнопкой для создания"""

    return InlineKeyboardMarkup(inline_keyboard=[
        *([
            InlineKeyboardButton(
                text=post_title,
                callback_data=CallbackSchoolPosts(action='post', post_id=post_id, offset=offset).pack()
            )
        ] for post_id, post_title in posts),
        [
            InlineKeyboardButton(
                text=" ",
                callback_data=CallbackSchoolPosts(action='menu', offset=left_offset).pack(),
                icon_custom_emoji_id=EmojiIdList.left if left_offset != offset else None
            ),
            InlineKeyboardButton(
                text=" ",
                callback_data=CallbackSchoolPosts(action='menu', offset=offset).pack(),
                icon_custom_emoji_id=EmojiIdList.update
            ),
            InlineKeyboardButton(
                text=" ",
                callback_data=CallbackSchoolPosts(action='menu', offset=right_offset).pack(),
                icon_custom_emoji_id=EmojiIdList.right if right_offset != offset else None
            )
        ],
        [
            InlineKeyboardButton(
                text="Создать публикацию",
                callback_data=CallbackSchoolPosts(action='create').pack(),
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


def post_buttons(url: str, post_id: int, offset: int) -> InlineKeyboardMarkup:
    """Меню поста"""

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Посмотреть",
                url=url,
                icon_custom_emoji_id=EmojiIdList.eyes
            )
        ],
        [
            InlineKeyboardButton(
                text="Редактировать",
                callback_data=CallbackSchoolPosts(action='edit', post_id=post_id).pack(),
                icon_custom_emoji_id=EmojiIdList.pencil
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить публикацию",
                callback_data=CallbackSchoolPosts(action='delete', post_id=post_id).pack(),
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=CallbackSchoolPosts(action='menu', offset=offset).pack(),
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ])


def back_button() -> ReplyKeyboardMarkup:
    """Клавиатурная кнопка Отмена"""

    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text="Отмена",
                icon_custom_emoji_id=EmojiIdList.back
            )
        ]
    ], resize_keyboard=True)


def optional_stage_buttons() -> ReplyKeyboardMarkup:
    """Клавиатурные кнопки для необязательного этапа создания поста"""

    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text="Пропустить",
                icon_custom_emoji_id=EmojiIdList.big_right
            )
        ],
        [
            KeyboardButton(
                text="Прошлый шаг",
                icon_custom_emoji_id=EmojiIdList.back
            )
        ],
        [
            KeyboardButton(
                text="Отмена",
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ]
    ], resize_keyboard=True)


def stage_buttons() -> ReplyKeyboardMarkup:
    """Клавиатурные кнопки для обязательного этапа создания поста"""

    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text="Прошлый шаг",
                icon_custom_emoji_id=EmojiIdList.back
            )
        ],
        [
            KeyboardButton(
                text="Отмена",
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ]
    ], resize_keyboard=True)


def stage_content_buttons() -> ReplyKeyboardMarkup:
    """Клавиатурные кнопки для этапа написания поста"""

    return ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(
                text="Прошлый шаг",
                icon_custom_emoji_id=EmojiIdList.back
            )
        ],
        [
            KeyboardButton(
                text="Опубликовать",
                icon_custom_emoji_id=EmojiIdList.activium
            )
        ],
        [
            KeyboardButton(
                text="Отмена",
                icon_custom_emoji_id=EmojiIdList.cross,
                style='danger'
            )
        ]
    ], resize_keyboard=True)
