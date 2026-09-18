from aiogram import Router
from ...enums.modules import ModuleList

from aiogram.types import Message
from aiogram.filters import Command
from ...enums.commands import CommandList

from aiogram.fsm.context import FSMContext

from ...enums.emoji import EmojiList
from aiogram.utils.formatting import Text, Bold, TextLink

from src.config.project_config import settings


__all__ = ['router']

router = Router(name=ModuleList.help)


@router.message(Command(CommandList.help))
async def _cmd_help(message: Message, state: FSMContext):
    """Команда /help с подробной информацией о приложении"""

    await state.clear()

    text = Text(
        "Приложение ", EmojiList.activium.value, settings.PROJECT_NAME_RU, " — ",
        "это удобный доступ к учебной информации в своем телефоне даже без интернета: "
        "расписанию, оценкам, мероприятиям и домашним заданиям, а также расширенному рейтингу в классе\n\n",

        Bold("Ключевые особенности:"), "\n",
        "- Расписание и домашнее всегда под рукой даже без интернета\n"
        "- Внеурочные занятия встроены в расписание\n"
        "- Напоминания о внеурочных занятиях\n"
        "- Уведомления о выставлении новых оценок\n"
        "- Удобный просмотр прикреплённых файлов к домашнему\n"
        "- Оценки, статистика и рейтинг в классе\n"
        "- Актуальные мероприятия и события\n\n",

        Bold("Безопасность и открытость"), "\n",
        "Код открыт на GitHub: ", TextLink("Activium", url=settings.GITHUB), ", ",
        TextLink("ActiviumServer", url=settings.GITHUB_SERVER), ". ",
        "Можно посмотреть реализацию авторизации, хранения данных, отправки уведомлений и в целом безопасности\n\n",
        "По любым вопросам: ", TextLink("поддержка", url=settings.AUTHOR_LINK)

    )

    await message.answer(**text.as_kwargs(), disable_web_page_preview=True)
