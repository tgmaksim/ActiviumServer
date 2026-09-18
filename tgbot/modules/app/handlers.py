from aiogram import Router
from ...enums.modules import ModuleList

from aiogram.types import Message
from aiogram.filters import Command
from ...enums.commands import CommandList

from aiogram.fsm.context import FSMContext

from ...enums.emoji import EmojiList
from aiogram.utils.formatting import Text

from .buttons import resources_buttons
from src.config.project_config import settings


__all__ = ['router']

router = Router(name=ModuleList.app)


@router.message(Command(CommandList.app))
async def _cmd_app(message: Message, state: FSMContext):
    """Ссылки на скачивание приложения и его исходный код"""

    await state.clear()

    text = Text(EmojiList.activium.value, settings.PROJECT_NAME_RU, " — ссылки")
    reply_markup = resources_buttons()

    await message.answer(**text.as_kwargs(), reply_markup=reply_markup)
