from aiogram import Router, F

from aiogram.filters import CommandStart
from aiogram.utils.formatting import Text, CustomEmoji
from aiogram.types import Message, CallbackQuery


__all__ = ['router']

router = Router()


start_text = Text(
    "Здравствуйте! ", CustomEmoji("👋", custom_emoji_id="5343984088493599366"), "\n",
    "Данный бот предназначен для подключения образовательных организаций к сервису Активиум ",
    CustomEmoji("🤓", custom_emoji_id="5406575351272872039"), "\n\n",

    "Подключить ОО: /school\n"
    "Меню администратора ОО: /menu\n"
    "Скачать можно по команде: /app\n"
    "Помощь: /help"
)


@router.message(CommandStart())
async def _cmd_start(message: Message):
    """Команда /start"""

    await message.answer(**start_text.as_kwargs())


@router.callback_query(F.data == "start")
async def _callback_start(callback_query: CallbackQuery):
    await callback_query.message.edit_text(**start_text.as_kwargs())
