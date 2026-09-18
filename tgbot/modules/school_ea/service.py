import json

from yarl import URL
from httpx import AsyncClient

from dnevnikru import AioDnevnikruApi
from datetime import timedelta, datetime, time, timezone

from src.config.project_config import settings
from src.utils.datetime import astimezone, datetime_now

from typing import Any, Callable

from ...enums.emoji import EmojiList
from aiogram.utils.formatting import Text

from ...enums.modules import ModuleList
from ...repositories.tgbot_uow import TgBotUnitOfWork
from ...schemas.service_result import ServiceResult, ServiceParams
from .constants import SHOWN_EA_LIMIT, levels
from .buttons import menu_buttons, level_buttons, ea_buttons, delete_buttons, edit_ea_buttons

from src.models import SchoolAdmin
from src.services.base_service import BaseService
from src.support.repositories.app_uow import AppUnitOfWork


__all__ = ['SchoolEAService']

IS_RUN_OUT_TYPE = bool
TEXT_TYPE = Text
BUTTONS_PARAMS_TYPE = list[tuple[str, dict[str, Any]]]
BACK_PARAMS_TYPE = tuple[str, dict[str, Any]]
RETURN_TYPE = tuple[IS_RUN_OUT_TYPE, TEXT_TYPE, BUTTONS_PARAMS_TYPE, BACK_PARAMS_TYPE]


class SchoolEAService(BaseService[AppUnitOfWork]):
    """Сервис для работы с внеурочными занятиями"""

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], tgbot_uow_factory: Callable[[], TgBotUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.tgbot_uow_factory = tgbot_uow_factory
        self.httpx_client = httpx_client

    async def menu(self) -> ServiceResult:
        data = {
            'level': 'group',
            'offset': 0
        }
        delete_data = {'filter': 'all'}

        async with self.tgbot_uow_factory() as tgbot_uow:
            entry = await tgbot_uow.tgbot_callback_data_repository.create_data(ModuleList.school_ea, 'list_ea', data)
            delete_entry = await tgbot_uow.tgbot_callback_data_repository.create_data(ModuleList.school_ea, 'delete', delete_data)

        text = Text(
            EmojiList.school.value, "Внеурочные занятия в образовательной организации"
        )
        reply_markup = menu_buttons(str(entry.key), str(delete_entry.key))

        return ServiceResult(text=text, reply_markup=reply_markup)

    async def list_ea(self, school_admin: SchoolAdmin, params: dict[str, Any]) -> ServiceResult:
        level: str = params['level']
        offset: int = params['offset']

        next_level = None if level == levels[-1] else levels[levels.index(level) + 1]
        previous_level = None if level == levels[0] else levels[levels.index(level) - 1]

        dnr = AioDnevnikruApi(self.httpx_client, school_admin.dnevnik_admin.dnevnik_token)

        since = datetime_now(school_admin.dnevnik_admin.timezone) - timedelta(days=32)

        is_run_out: bool  # Данные закончились
        text: Text  # Текст сообщения
        buttons_params: list[tuple[str, dict[str, Any]]]  # Текст и данные кнопки
        back_params: tuple[str, dict[str, Any]]  # action и params кнопки назад

        if level == 'group':
            is_run_out, text, buttons_params, back_params = await self._level_group(
                school_admin, since, offset, dnr, next_level
            )

        elif level == 'subject_place':
            group_id: int = params['group_id']
            group_name: str = params['group_name']

            is_run_out, text, buttons_params, back_params = await self._level_subject_place(
                school_admin, since, offset, group_id, group_name, next_level, previous_level
            )

        elif level == 'extracurricular_activity':
            group_id: int = params['group_id']
            group_name: str = params['group_name']
            subject: str = params['subject']
            place: str = params['place']

            is_run_out, text, buttons_params, back_params = await self._level_extracurricular_activity(
                school_admin, since, offset, group_id, group_name, subject, place, next_level, previous_level
            )

        elif level == 'menu':
            group_name: str = params['group_name']
            ea_id: int = params['ea_id']

            return await self._level_menu(school_admin, group_name, ea_id, previous_level)
        else:
            return ServiceResult(success=False, alert="Произошла непредвиденная ошибка [lnf]")  # level not found

        text = Text(
            EmojiList.school.value, text
        )

        right_offset = offset + SHOWN_EA_LIMIT if not is_run_out else offset
        left_offset = max(0, offset - SHOWN_EA_LIMIT)

        nav_buttons_params = [
            {**params, 'offset': left_offset},
            {**params, 'offset': offset},
            {**params, 'offset': right_offset}
        ]

        async with self.tgbot_uow_factory() as tgbot_uow:
            entries = await tgbot_uow.tgbot_callback_data_repository.create_many_data(
                ModuleList.school_ea, 'list_ea',
                [button[1] for button in buttons_params] + nav_buttons_params,
            )

            back_entry = await tgbot_uow.tgbot_callback_data_repository.create_data(
                ModuleList.school_ea, back_params[0], back_params[1]
            )

            delete_entry = None
            if level == 'extracurricular_activity':
                delete_entry = await tgbot_uow.tgbot_callback_data_repository.create_data(
                    ModuleList.school_ea, 'delete',
                    {**params, 'filter': 'list_ea'}
                )

        reply_markup = level_buttons(
            [(buttons_params[i][0], str(entries[i].key)) for i in range(len(buttons_params))],
            [str(entries[i].key) for i in range(len(buttons_params), len(buttons_params) + len(nav_buttons_params))],
            [right_offset != offset, True, left_offset != offset],
            delete_entry and str(delete_entry.key),
            (back_params[0], str(back_entry.key))
        )

        return ServiceResult(text=text, reply_markup=reply_markup)

    async def _level_group(self, school_admin: SchoolAdmin, since: datetime, offset: int, dnr: AioDnevnikruApi, next_level: str) -> RETURN_TYPE:
        async with self.uow_factory() as uow:
            groups_id = await (
                uow.extracurricular_activity_repository
                .get_groups(
                    school_admin.dnevnik_admin.school_id, since, offset,
                    limit=SHOWN_EA_LIMIT + 1  # Для проверки существования следующего класса после лимита
                )
            )

        is_run_out = len(groups_id) <= SHOWN_EA_LIMIT
        groups_id = groups_id[:SHOWN_EA_LIMIT]

        groups = await dnr.get_groups(groups_id) if groups_id else []

        text = Text(
            "Выберите учебную группу (класс), в котором проводятся внеурочные занятия"
        )

        buttons_params = [
            (
                group['group']['fullName'],
                {
                    'level': next_level,
                    'offset': 0,
                    'group_id': group['group']['id'],
                    'group_name': group['group']['fullName']
                }
            )
            for group in groups
        ]

        back_params = ('menu', {})

        return is_run_out, text, buttons_params, back_params

    async def _level_subject_place(self, school_admin: SchoolAdmin, since: datetime, offset: int, group_id: int, group_name: str, next_level: str, previous_level: str) -> RETURN_TYPE:
        async with self.uow_factory() as uow:
            subjects_places = await uow.extracurricular_activity_repository.get_subject_place_by_group(
                school_admin.dnevnik_admin.school_id, group_id, since, offset,
                limit=SHOWN_EA_LIMIT + 1  # Для проверки существования следующего предмета с кабинетом после лимита
            )

        is_run_out = len(subjects_places) <= SHOWN_EA_LIMIT
        subjects_places = subjects_places[:SHOWN_EA_LIMIT]

        text = Text(
            f"Выберите предмет и кабинет, в котором проводятся внеурочные занятия у {group_name}"
        )

        buttons_params = [
            (
                f"{subject} - {place}",
                {
                    'level': next_level,
                    'offset': 0,
                    'group_id': group_id,
                    'group_name': group_name,
                    'subject': subject,
                    'place': place
                }
            )
            for subject, place in subjects_places
        ]

        back_params = (
            'list_ea',
            {
                'level': previous_level,
                'offset': 0
            }
        )

        return is_run_out, text, buttons_params, back_params

    async def _level_extracurricular_activity(self, school_admin: SchoolAdmin, since: datetime, offset: int, group_id: int, group_name: str, subject: str, place: str, next_level: str, previous_level: str) -> RETURN_TYPE:
        async with self.uow_factory() as uow:
            extracurricular_activities = await uow.extracurricular_activity_repository.get_extracurricular_activities_by_subject_place(
                school_admin.dnevnik_admin.school_id, group_id, subject, place, since, offset,
                limit=SHOWN_EA_LIMIT + 1  # Для проверки существования следующего внеурочного занятия после лимита
            )

        is_run_out = len(extracurricular_activities) <= SHOWN_EA_LIMIT
        extracurricular_activities = extracurricular_activities[:SHOWN_EA_LIMIT]

        text = Text(
            f"Выберите время проведения внеурочного занятия у {group_name} по {subject} в {place}"
        )

        buttons_params = [
            (
                astimezone(ea.start_time, school_admin.dnevnik_admin.timezone).strftime('%e %b. в %H:%M'),
                {
                    'level': next_level,
                    'offset': 0,
                    'group_id': group_id,
                    'group_name': group_name,
                    'subject': subject,
                    'place': place,
                    'ea_id': ea.ea_id
                }
            )
            for ea in extracurricular_activities
        ]

        back_params = (
            'list_ea',
            {
                'level': previous_level,
                'offset': 0,
                'group_id': group_id,
                'group_name': group_name
            }
        )

        return is_run_out, text, buttons_params, back_params

    async def _level_menu(self, school_admin: SchoolAdmin, group_name: str, ea_id: int, previous_level: str) -> ServiceResult:
        async with self.uow_factory() as uow:
            extracurricular_activity = await uow.extracurricular_activity_repository.get_extracurricular_activity(
                school_admin.dnevnik_admin.school_id, ea_id)

        if extracurricular_activity is None:
            return ServiceResult(success=False, alert="Внеурочное занятие не найдено, вернитесь назад")

        text = Text(
            EmojiList.school.value, "Внеурочное занятие ",
            f"у {group_name} по {extracurricular_activity.subject} в {extracurricular_activity.place} "
            f"{extracurricular_activity.start_time.strftime('%e %b.')} ({extracurricular_activity.hours['string']})"
        )

        callback_data = {
            'ea_id': ea_id
        }
        delete_data = {**callback_data, 'filter': 'ea'}
        back_data = {
            'level': previous_level,
            'offset': 0,
            'group_id': extracurricular_activity.group_id,
            'group_name': group_name,
            'subject': extracurricular_activity.subject,
            'place': extracurricular_activity.place
        }

        async with self.tgbot_uow_factory() as tgbot_uow:
            edit_entry = await tgbot_uow.tgbot_callback_data_repository.create_data(ModuleList.school_ea, 'edit', callback_data)
            delete_entry = await tgbot_uow.tgbot_callback_data_repository.create_data(ModuleList.school_ea, 'delete', delete_data)
            back_entry = await tgbot_uow.tgbot_callback_data_repository.create_data(ModuleList.school_ea, 'list_ea', back_data)

        reply_markup = ea_buttons(str(edit_entry.key), str(delete_entry.key), str(back_entry.key))

        return ServiceResult(text=text, reply_markup=reply_markup)

    @staticmethod
    async def _get_group_name(dnr: AioDnevnikruApi, group_id: int) -> str:
        group = await dnr.get_group(group_id)
        return group['fullName']

    async def delete(self, params: dict[str, Any]) -> ServiceResult:
        async with self.tgbot_uow_factory() as tgbot_uow:
            entry = await tgbot_uow.tgbot_callback_data_repository.create_data(ModuleList.school_ea, 'confirm_delete', params)

        delete_filter = params['filter']

        if delete_filter == 'all':
            count = "ВСЕ внеурочные занятия"
        elif delete_filter == 'list_ea':
            count = "все внеурочные занятия по предмету в классе"
        elif delete_filter == 'ea':
            count = "одно внеурочное занятие"
        else:
            raise RuntimeError('delete filter not found')

        text = Text(
            EmojiList.question.value, f"Вы уверены, что хотите удалить {count}?"
        )
        reply_markup = delete_buttons(str(entry.key))

        return ServiceResult(text=text, reply_markup=reply_markup)

    async def confirm_delete(self, school_admin: SchoolAdmin, params: dict[str, Any]) -> ServiceResult:
        delete_filter = params['filter']

        async with self.uow_factory() as uow:
            if delete_filter == 'all':
                await uow.extracurricular_activity_repository.delete_all_school(school_admin.dnevnik_admin.school_id)
            elif delete_filter == 'list_ea':
                group_id: int = params['group_id']
                subject: str = params['subject']
                place: str = params['place']

                await uow.extracurricular_activity_repository.delete_extracurricular_activities_by_subject_place(
                    school_admin.dnevnik_admin.school_id, group_id, subject, place
                )
            elif delete_filter == 'ea':
                ea_id: int = params['ea_id']

                await uow.extracurricular_activity_repository.delete_extracurricular_activity(
                    school_admin.dnevnik_admin.school_id, ea_id
                )
            else:
                raise RuntimeError('delete filter not found')

        return await self.menu()

    async def edit_ea(self, school_admin: SchoolAdmin, params: dict[str, Any]) -> ServiceResult:
        ea_id = params['ea_id']

        async with self.uow_factory() as uow:
            extracurricular_activity = await (
                uow.extracurricular_activity_repository
                .get_extracurricular_activity(school_admin.dnevnik_admin.school_id, ea_id)
            )

        if extracurricular_activity is None:
            return ServiceResult(success=False, alert="Внеурочное занятие не найдено, вернитесь назад")

        web_app_url = str(
            URL(settings.URL_FOR_TG)
            .joinpath("tg-webapp", "extracurricular_activity", "edit")
            .update_query(
                subject=extracurricular_activity.subject,
                place=extracurricular_activity.place,
                date=extracurricular_activity.start_time.date().isoformat(),
                start_time=extracurricular_activity.hours['start'],
                end_time=extracurricular_activity.hours['end']
            )
        )

        text = Text(
            EmojiList.pencil.value, "Вы можете изменить данные конкретного внеурочного занятия или отменить операцию"
        )
        reply_markup = edit_ea_buttons(web_app_url)

        return ServiceResult(text=text, reply_markup=reply_markup, service_params=ServiceParams(delete_message=True))

    async def cancel_edit_ea(self) -> ServiceResult:
        answer = await self.menu()
        answer.service_params.delete_keyboard = True
        return answer

    async def update_ea(self, school_admin: SchoolAdmin, ea_id: int, data: str) -> ServiceResult:
        data = json.loads(data)

        start = time.fromisoformat(data['start_time'])
        end = time.fromisoformat(data['end_time'])

        start_str = start.strftime('%H:%M')
        end_str = end.strftime('%H:%M')

        start_time = datetime.fromisoformat(data['date']).replace(hour=start.hour, minute=start.minute)
        start_time = start_time.replace(tzinfo=timezone(timedelta(seconds=school_admin.dnevnik_admin.timezone)))

        async with self.uow_factory() as uow:
            ea = await uow.extracurricular_activity_repository.edit(
                school_admin.dnevnik_admin.school_id, ea_id,
                subject=data['subject'],
                place=data['place'],
                start_time=start_time,
                hours={
                    'start': start_str,
                    'end': end_str,
                    'string': f"{start_str} - {end_str}"
                }
            )

        if ea is None:
            answer = await self.menu()
        else:
            dnr = AioDnevnikruApi(self.httpx_client, school_admin.dnevnik_admin.dnevnik_token)
            group_name = await self._get_group_name(dnr, ea.group_id)

            answer = await self._level_menu(school_admin, group_name, ea_id, 'extracurricular_activity')

        answer.service_params.delete_keyboard = True
        return answer
