from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, CustomEmoji, Bold, TextLink

from src.config.project_config import settings


__all__ = ['router']

router = Router()


@router.message(Command('help'))
async def _cmd_help(message: Message):
    """Команда /help с подробной информацией о приложении"""

    await message.answer(**Text(
        "Приложение ", CustomEmoji("🤓", custom_emoji_id="5406575351272872039"), " Активиум — ",
        "это не просто мобильная версия Дневник.ру, это удобный доступ к учебной информации в своем телефоне даже без "
        "интернета: расписанию, оценкам, мероприятиям и домашним заданиям, а также расширенному рейтингу в классе\n\n",

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
        "Можно посмотреть реализацию авторизации, хранения данных, отправки уведомлений и в целом безопасности\n\n"
        
        "По любым вопросам: ", TextLink("поддержка", url=settings.AUTHOR_LINK)
    ).as_kwargs(), disable_web_page_preview=True)
