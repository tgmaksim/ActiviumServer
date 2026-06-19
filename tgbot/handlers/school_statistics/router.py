import time

from pathlib import Path
from asyncio import gather

from aiogram import Router, F

from aiogram.utils.formatting import Text, CustomEmoji

from datetime import datetime, UTC
from src.utils.datetime import astimezone

from src.dependencies.httpx import get_httpx_client
from dnevnikru import AioDnevnikruApi, BaseDnevnikruException

from src.repositories.statistic_repository import StatName

from src.config.project_config import settings

from .repository import SchoolStatisticsRepository
from src.dependencies.uow import get_app_uow_factory

from .service import create_admin_stats

from ...utils.auth import check_school_admin
from ...utils.school_admin_error import SchoolAdminError

from aiogram.types import (
    FSInputFile,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


__all__ = ['router']

router = Router()

uow_factory = get_app_uow_factory()


@router.callback_query(F.data == "admin_stats")
async def _admin_stats(callback_query: CallbackQuery):
    """Просмотр статистики по приложению в образовательной организации"""

    async with uow_factory() as uow:
        await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)

        text = Text(
            CustomEmoji("📊", custom_emoji_id="5231200819986047254"),
            f"Статистика {settings.PROJECT_NAME_RU} в ОО\n\n",

            f"Вы можете запросить отчет со статистикой пользования {settings.PROJECT_NAME_RU} "
            "по Вашей образовательной организацией. В отчете будут графики и диаграммы по динамике числа "
            "зарегистрированных и активных пользователей, а также по отношению детей и родителей\n\n",

            "Для составления отчета потребуется немного времени"
        )

        await callback_query.message.edit_text(
            **text.as_kwargs(),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Сформировать отчет", callback_data="create_admin_stats", icon_custom_emoji_id="5445255358589182162")],
                [InlineKeyboardButton(text="Назад", callback_data="menu", icon_custom_emoji_id="5467864676320681402")]
            ])
        )


@router.callback_query(F.data == "create_admin_stats")
async def _create_admin_stats(callback_query: CallbackQuery):
    """Формирование отчета со статистикой для администратора образовательной организации"""

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)

        relative_path = ('temp', 'school_statistics', str(school_admin.dnevnik_admin.school_id), 'statistics.pdf')
        path = Path(settings.WWW_PATH, *relative_path)

        now = astimezone(datetime.now(UTC), school_admin.dnevnik_admin.timezone)
        start_period = now.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0)  # 1 сентября
        if start_period > now:
            start_period = start_period.replace(year=start_period.year - 1)  # Прошедшее 1 сентября

        dnr = AioDnevnikruApi(get_httpx_client(), school_admin.dnevnik_admin.dnevnik_token)

        school_statistics_repository = SchoolStatisticsRepository(
            uow.queue,
            school_admin,
            dnr,
            start_period,
            now
        )

        # Получение данных для показа
        try:
            (cumulative_users, daily_registration), (daily_actions, unique_users_daily), all_users, class_distribution = await gather(
                school_statistics_repository.get_users_stats(),
                school_statistics_repository.get_daily_actions(),
                school_statistics_repository.get_all_users(),
                school_statistics_repository.get_class_distribution()
            )
        except BaseDnevnikruException as e:
            if not await uow.school_admin_repository.check_auth(school_admin.user_id, dnr):
                raise SchoolAdminError(user_id=school_admin.user_id) from e
            raise
        except Exception:
            await callback_query.answer("Произошла ошибка при получении данных", show_alert=True)
            raise

        # Создание листа с графиками и диаграммами
        try:
            start = time.monotonic()
            create_admin_stats(
                path,
                cumulative_users,
                all_users,
                daily_registration,
                daily_actions,
                unique_users_daily,
                class_distribution
            )
            end = time.monotonic()
        except Exception:
            await callback_query.answer("Произошла ошибка при создании отчета", show_alert=True)
            raise

        await callback_query.message.delete()

        # Отправка документа и удаление файла
        await callback_query.message.answer_document(FSInputFile(path))
        path.unlink(missing_ok=True)

        await callback_query.message.answer(
            f"Вернуться в меню",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="menu", icon_custom_emoji_id="5467864676320681402")]
            ])
        )

        # Запись лога и статистики
        await uow.log_repository.add_log(
            ip='tgbot',
            path='create_admin_stats',
            value=f"Create statistics ({end - start} seconds)"
        )
        await uow.statistic_repository.add_statistic(None, StatName.createAdminStatistics)
