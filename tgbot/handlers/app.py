from aiogram import Router

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Text, CustomEmoji
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from src.config.project_config import settings


__all__ = ['router']

router = Router()


@router.message(Command('app'))
async def _cmd_app(message: Message, state: FSMContext):
    """Ссылки на скачивание приложения и его исходный код"""

    await state.clear()

    await message.answer(
        **Text(
            CustomEmoji("🤓", custom_emoji_id="5406575351272872039"),
            " ", settings.PROJECT_NAME_RU, " — ссылки"
        ).as_kwargs(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Скачать", icon_custom_emoji_id="5197404349399054325", url=settings.URL)],
            [InlineKeyboardButton(text="Исходный код", icon_custom_emoji_id="4961044117187462239", url=settings.GITHUB)]
        ])
    )
