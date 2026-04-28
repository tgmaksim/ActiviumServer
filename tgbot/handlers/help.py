from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command

from src.config.project_config import settings


__all__ = ['router']

router = Router()


@router.message(Command('help'))
async def _cmd_help(message: Message):
    await message.answer("Приложение <tg-emoji emoji-id=\"5406575351272872039\">🤓</tg-emoji> Активиум — "
                         "это не просто мобильная версия Дневник.ру, это удобный доступ к учебной "
                         "информации в своем телефоне даже без интернета: расписанию, оценкам, мероприятиям и домашним "
                         "заданиям, а также расширенному рейтингу в классе\n\n"
                         
                         "<b>Ключевые особенности:</b>\n"
                         "- Расписание и домашнее всегда под рукой даже без интернета\n"
                         "- Внеурочные занятия встроены в расписание\n"
                         "- Напоминания о внеурочных занятиях\n"
                         "- Уведомления о выставлении новых оценок\n"
                         "- Удобный просмотр прикреплённых файлов к домашнему\n"
                         "- Оценки, статистика и рейтинг в классе\n"
                         "- Актуальные мероприятия и события\n\n"
                         
                         "<b>Безопасность и открытость</b>\n"
                         f"Код открыт на GitHub: <a href='{settings.GITHUB}'>Actvium</a>, "
                         f"<a href='{settings.GITHUB_SERVER}'>ActviumServer</a>. Можно посмотреть реализацию "
                         "авторизации, хранения данных, отправки уведомлений и в целом безопасности\n\n"
                         
                         f"По любым вопросам: <a href='{settings.AUTHOR_LINK}'>поддержка</a>",
                         disable_web_page_preview=True)
