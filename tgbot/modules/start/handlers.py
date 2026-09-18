from aiogram import Router

from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext

from src.config.project_config import settings

from tgbot.enums.emoji import EmojiList
from aiogram.utils.formatting import Text
from tgbot.enums.modules import ModuleList
from tgbot.enums.commands import CommandList


__all__ = ['router']

router = Router(name=ModuleList.start)


@router.message(CommandStart())
async def _cmd_start(message: Message, state: FSMContext):
    """Команда /start"""

    await state.clear()

    text = Text(
        "Здравствуйте! ", EmojiList.hello.value, "\n",
        f"Данный бот предназначен для подключения образовательных организаций к сервису {settings.PROJECT_NAME_RU} ",
        EmojiList.activium.value, "\n\n",

        f"Подключить ОО: /{CommandList.school}\n"
        f"Меню администратора ОО: /{CommandList.menu}\n"
        f"Скачать можно по команде: /{CommandList.app}\n"
        f"Помощь: /{CommandList.help}"
    )

    await message.answer(**text.as_kwargs(), reply_markup=ReplyKeyboardRemove())
