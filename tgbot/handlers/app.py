from aiogram import Router

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..config import settings


__all__ = ['router']

router = Router()


@router.message(Command('app'))
async def _cmd_app(message: Message):
    await message.answer(
        "<tg-emoji emoji-id=\"5406575351272872039\">🤓</tg-emoji> Активиум — ссылки",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Скачать", icon_custom_emoji_id="5197404349399054325", url=settings.URL)],
            [InlineKeyboardButton(text="Исходный код", icon_custom_emoji_id="4961044117187462239", url=settings.GITHUB)]]
        ))
