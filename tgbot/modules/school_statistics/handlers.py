from aiogram import Router
from aiogram.utils.formatting import Text
from aiogram.types import FSInputFile, CallbackQuery

from src.models import SchoolAdmin
from src.config.project_config import settings

from .buttons import menu_buttons, back_button
from ...callbacks.school_stats import CallbackSchoolStats

from ...enums.emoji import EmojiList
from .service import SchoolStatsService
from ...enums.modules import ModuleList
from ...dependencies.services import ModuleService


__all__ = ['router']

router = Router(name=ModuleList.school_stats)


@router.callback_query(CallbackSchoolStats.filter_action('menu'), flags={'auth': True})
async def _admin_stats_menu(callback_query: CallbackQuery):
    """Просмотр статистики по приложению в образовательной организации"""

    text = Text(
        EmojiList.histogram.value, f"Статистика {settings.PROJECT_NAME_RU} в ОО\n\n",

        f"Вы можете запросить отчет со статистикой пользования {settings.PROJECT_NAME_RU} "
        "по Вашей образовательной организацией. В отчете будут графики и диаграммы по динамике числа "
        "зарегистрированных и активных пользователей, а также по отношению детей и родителей\n\n",

        "Для составления отчета потребуется немного времени"
    )

    reply_markup = menu_buttons()

    await callback_query.message.edit_text(**text.as_kwargs(), reply_markup=reply_markup)


@router.callback_query(CallbackSchoolStats.filter_action('create'), ModuleService(SchoolStatsService), flags={'full_auth': True})
async def _create_admin_stats(callback_query: CallbackQuery, service: SchoolStatsService, school_admin: SchoolAdmin):
    """Формирование отчета со статистикой для администратора образовательной организации"""

    try:
        path = await service.create_stats(school_admin)
    except Exception as e:
        if len(e.args) == 1:
            if e.args[0] == 'get data':
                await callback_query.answer("Произошла ошибка при получении данных", show_alert=True)
            elif e.args[0] == 'create':
                await callback_query.answer("Произошла ошибка при создании отчета", show_alert=True)

        raise

    await callback_query.message.delete()

    # Отправка документа и удаление файла
    await callback_query.message.answer_document(FSInputFile(path))
    path.unlink(missing_ok=True)

    text = Text(
        "Вернуться в меню"
    )
    reply_markup = back_button()

    await callback_query.message.answer(**text.as_kwargs(), reply_markup=reply_markup)
