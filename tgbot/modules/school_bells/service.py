import re
import json

from yarl import URL
from datetime import time
from typing import Optional

from .constants import weekdays, months
from .dicts import InputBellsWebAppDataType
from .buttons import bells_buttons, bell_buttons, create_or_edit_buttons

from ...enums.emoji import EmojiList
from aiogram.utils.formatting import Text
from ...schemas.service_result import ServiceResult, ServiceParams

from src.models import SchoolAdmin
from src.config.project_config import settings
from src.services.base_service import BaseService
from src.support.repositories.app_uow import AppUnitOfWork


__all__ = ['SchoolBellsService']


class SchoolBellsService(BaseService[AppUnitOfWork]):
    """Сервис для работы с расписанием звонков"""

    async def school_bells(self, school_admin: SchoolAdmin) -> ServiceResult:
        async with self.uow_factory() as uow:
            bells = await uow.hour_repository.get_school_hours(school_admin.dnevnik_admin.school_id)

        text = Text(
            EmojiList.bell.value, "Звонковые расписания\n\n",

            f"Вы можете изменить звонковое расписание, которое будет использоваться в приложении {settings.PROJECT_NAME_RU}. "
            "По умолчанию используются данные из Дневника.ру, но если расписание требует более гибкой настройки, "
            "то это можно сделать здесь\n\n"

            "Добавляйте отдельное расписание для каждого месяца и дня недели или объединяйте их в случае совпадения"
        )

        reply_markup = bells_buttons([
            (bell.hour_id, ', '.join([weekdays[weekday] for weekday in bell.weekdays]), self._months_format(bell.months))
            for bell in bells
        ])

        return ServiceResult(text=text, reply_markup=reply_markup)

    @classmethod
    def _months_format(cls, bell_months: list[int]) -> str:
        """Форматирование списка месяцев"""

        unique_months = set(bell_months)

        # Если выбраны абсолютно все месяцы года
        if len(unique_months) == 12:
            return "январь - декабрь"

        starts: list[int] = []
        for m in unique_months:
            prev_month = 12 if m == 1 else m - 1
            if prev_month not in unique_months:
                starts.append(m)

        intervals: list[tuple[int, int, int]] = []
        for start in starts:
            curr = start
            length = 1
            while True:
                nxt_month = (curr % 12) + 1  # Переход 12 -> 1
                if nxt_month in unique_months:
                    curr = nxt_month
                    length += 1
                else:
                    break
            intervals.append((start, curr, length))

        intervals.sort(key=lambda x: x[0])

        result_parts = []
        for start, end, length in intervals:
            if length >= 2:  # Отрезок из 2 и более месяцев пишется через тире
                result_parts.append(f"{months[start - 1]} - {months[end - 1]}")
            else:
                result_parts.append(months[start - 1])

        return ', '.join(result_parts)

    async def school_bell(self, school_admin: SchoolAdmin, hour_id: int) -> ServiceResult:
        async with self.uow_factory() as uow:
            bell = await uow.hour_repository.get_school_hour(school_admin.dnevnik_admin.school_id, hour_id)

        if bell is None:
            return await self.school_bells(school_admin)

        text = Text(
            EmojiList.bell.value, "Звонковое расписание\n\n",

            "Настроено на следующее время:\n"
            f"Месяца: {self._months_format(bell.months)}\n"
            f"Дни недели: {', '.join([weekdays[weekday] for weekday in bell.weekdays])}\n\n"
            
            "Расписание:\n",
            '\n'.join([hour['string'] for hour in bell.hours])
        )

        reply_markup = bell_buttons(bell.hour_id)

        return ServiceResult(text=text, reply_markup=reply_markup)

    async def create_or_edit_school_bell(self, school_admin: SchoolAdmin, hour_id: Optional[int]) -> ServiceResult:
        async with self.uow_factory() as uow:
            bell = hour_id and await uow.hour_repository.get_school_hour(school_admin.dnevnik_admin.school_id, hour_id)

        if bell is None and hour_id is not None:  # Расписание не найдено
            return await self.school_bells(school_admin)

        web_app_url = str(
            URL(settings.URL_FOR_TG)
            .joinpath("tg-webapp", "bells")
            .update_query(**(
                {
                    'bells': json.dumps(bell.hours),
                    'months': json.dumps(bell.months),
                    'weekdays': json.dumps(bell.weekdays)
                } if bell else {'none': 'none'}
            ))
        )


        text = Text(
            "Откройте редактор по кнопке ниже и измените расписание"
        )
        reply_markup = create_or_edit_buttons(web_app_url)

        return ServiceResult(text=text, reply_markup=reply_markup, service_params=ServiceParams(delete_message=True))

    async def cancel_create_or_edit_bell(self, school_admin: SchoolAdmin, hour_id: Optional[int]) -> ServiceResult:
        if hour_id is None:
            answer = await self.school_bells(school_admin)
        else:
            answer = await self.school_bell(school_admin, hour_id)

        answer.service_params.delete_keyboard = True
        return answer

    async def create_or_edit_bell(self, school_admin: SchoolAdmin, hour_id: Optional[int], data: str) -> ServiceResult:
        try:
            input_data: InputBellsWebAppDataType = json.loads(data)
            set_months = set(input_data['months'])
            set_weekdays = set(input_data['weekdays'])
            bells = input_data['bells']
        except (KeyError, TypeError, json.decoder.JSONDecodeError):
            error_text = Text(
                "Произошла ошибка при получении данных от редактора, попробуйте еще раз"
            )
            return ServiceResult(success=False, text=error_text)

        if not set_months or not set_weekdays:
            error_text = Text(
                "Расписание должно быть привязано к хотя бы одному месяцу и дню недели, попробуйте еще раз"
            )
            return ServiceResult(success=False, text=error_text)

        if len(bells) > 20:
            error_text = Text(
                "Расписание слишком длинное, попробуйте еще раз"
            )
            return ServiceResult(success=False, text=error_text)

        bells.sort(key=lambda b: time.fromisoformat(b['start']))

        time_format = re.compile(r'\d\d:\d\d')
        for i, bell in enumerate(bells):
            if not re.fullmatch(time_format, bell['start']) or not re.fullmatch(time_format, bell['end']):
                error_text = Text(
                    "Произошла ошибка при получении данных от редактора, попробуйте еще раз"
                )
                return ServiceResult(success=False, text=error_text)

            if i != 0:
                if time.fromisoformat(bells[i - 1]['end']) >= time.fromisoformat(bell['start']):
                    error_text = Text(
                        "Следующий урок должен начинаться позже окончания предыдущего, попробуйте еще раз"
                    )
                    return ServiceResult(success=False, text=error_text)

            if time.fromisoformat(bell['start']) >= time.fromisoformat(bell['end']):
                error_text = Text(
                    "Время начала должно быть раньше времени окончания, попробуйте еще раз"
                )
                return ServiceResult(success=False, text=error_text)

        async with self.uow_factory() as uow:
            school_hours = await uow.hour_repository.get_school_hours(school_admin.dnevnik_admin.school_id)

            for hour in school_hours:
                if hour.hour_id != hour_id and set(hour.months) & set_months and set(hour.weekdays) & set_weekdays:
                    error_text = Text(
                        "У нового расписания есть пересечение с другими, попробуйте еще раз"
                    )
                    return ServiceResult(success=False, text=error_text)

            if hour_id is None:
                await uow.hour_repository.create_school_hour(
                    school_admin.dnevnik_admin.school_id,
                    list(set_months),
                    list(set_weekdays),
                    bells
                )
            else:
                await uow.hour_repository.update_school_hour(
                    school_admin.dnevnik_admin.school_id,
                    hour_id,
                    list(set_months),
                    list(set_weekdays),
                    bells
                )

        answer = await self.school_bells(school_admin)
        answer.service_params.delete_keyboard = True

        return answer

    async def delete_school_bell(self, school_admin: SchoolAdmin, hour_id: int) -> ServiceResult:
        async with self.uow_factory() as uow:
            await uow.hour_repository.delete_school_hour(school_admin.dnevnik_admin.school_id, hour_id)

        return await self.school_bells(school_admin)
