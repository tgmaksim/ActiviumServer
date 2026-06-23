import re
import json

from yarl import URL
from datetime import time
from typing import Optional, TypedDict

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ..utils.auth import check_school_admin

from ..utils.message_model import MessageModel
from aiogram.utils.formatting import Text, CustomEmoji

from src.models.hours_type import HoursType
from src.config.project_config import settings
from src.dependencies.uow import get_app_uow_factory
from src.support.repositories.app_uow import AppUnitOfWork

from aiogram.types import (
    Message,
    WebAppInfo,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


__all__ = ['router']

router = Router()

uow_factory = get_app_uow_factory()

weekdays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
months = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]


class InputBellsWebAppDataType(TypedDict):
    months: list[int]
    weekdays: list[int]
    bells: list[HoursType]


class BellsStatesGroup(StatesGroup):
    """Группа состояний при изменении звонкового расписания образовательной организации"""

    create_or_update_bells = State('create_or_update_bells')
    """Ожидание сообщения от Web App с данными"""


@router.callback_query(F.data == "school_bells")
async def _school_bells(callback_query: CallbackQuery):
    """Общее меню звонкового распирания"""

    async with uow_factory() as uow:
        answer = await bells_menu(uow, callback_query.from_user.id)

        await callback_query.message.edit_text(**answer)


async def bells_menu(uow: AppUnitOfWork, user_id: int) -> MessageModel:
    """Список со звонковыми расписаниями образовательной организации"""

    school_admin = await check_school_admin(user_id, uow.school_admin_repository)

    bells = await uow.hour_repository.get_school_hours(school_admin.dnevnik_admin.school_id)

    buttons = [[InlineKeyboardButton(
        text=f"На {', '.join([weekdays[weekday] for weekday in bell.weekdays])} "
             f"за {months_format(bell.months)}",
        callback_data=f"school_bell|{bell.hour_id}"
    )] for bell in bells]

    buttons.append([InlineKeyboardButton(text="Добавить расписание", callback_data="add_school_bell", icon_custom_emoji_id="5397916757333654639")])
    buttons.append([InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="menu")])

    return MessageModel(
        text=Text(
            CustomEmoji("🔔", custom_emoji_id="5458603043203327669"), " Звонковые расписания\n\n",

            f"Вы можете изменить звонковое расписание, которое будет использоваться в приложении {settings.PROJECT_NAME_RU}. "
            "По умолчанию используются данные из Дневника.ру, но если расписание требует более гибкой настройки, "
            "то это можно сделать здесь\n\n"
            
            "Добавляйте отдельное расписание для каждого месяца и дня недели или объединяйте их в случае совпадения"
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


def months_format(bell_months: list[int]) -> str:
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


@router.callback_query(F.data.startswith("school_bell|"))
async def _school_bell_menu(callback_query: CallbackQuery):
    """Меню конкретного звонкового расписания"""

    hour_id = int(callback_query.data.split("|")[1])

    async with uow_factory() as uow:
        answer = await bell_menu(uow, callback_query.from_user.id, hour_id)

        await callback_query.message.edit_text(**answer)


async def bell_menu(uow: AppUnitOfWork, user_id: int, hour_id: int) -> MessageModel:
    """Удаление, изменение конкретного звонкового расписания"""

    school_admin = await check_school_admin(user_id, uow.school_admin_repository)

    hour = await uow.hour_repository.get_school_hour(school_admin.dnevnik_admin.school_id, hour_id)
    if hour is None:
        return await bells_menu(uow, user_id)

    return MessageModel(
        text=Text(
            CustomEmoji("🔔", custom_emoji_id="5458603043203327669"), " Звонковое расписание\n\n",

            "Настроено на следующее время:\n"
            f"Месяца: {months_format(hour.months)}\n"
            f"Дни недели: {', '.join([weekdays[weekday] for weekday in hour.weekdays])}\n\n"
            
            "Расписание:\n",
            '\n'.join([school_hour['string'] for school_hour in hour.hours])
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Редактировать расписание", callback_data=f"edit_school_bell|{hour_id}", icon_custom_emoji_id="5395444784611480792")],
            [InlineKeyboardButton(text="Удалить расписание", callback_data=f"delete_school_bell|{hour_id}", icon_custom_emoji_id="5210952531676504517")],
            [InlineKeyboardButton(text="Назад", callback_data="school_bells", icon_custom_emoji_id="5467864676320681402")]
        ])
    )


@router.callback_query(F.data.startswith("edit_school_bell|"))
async def _edit_school_bell(callback_query: CallbackQuery, state: FSMContext):
    """Редактирование звонкового расписания"""

    hour_id = int(callback_query.data.split("|")[1])

    async with uow_factory() as uow:
        answer = await create_or_edit_bell(uow, callback_query.from_user.id, state, hour_id)

        await callback_query.message.delete()
        await callback_query.message.answer(**answer)


async def create_or_edit_bell(uow: AppUnitOfWork, user_id: int, state: FSMContext, hour_id: Optional[int] = None) -> MessageModel:
    """Создание или редактирование звонкового расписания"""

    school_admin = await check_school_admin(user_id, uow.school_admin_repository, check_auth=True)

    hour = hour_id and await uow.hour_repository.get_school_hour(school_admin.dnevnik_admin.school_id, hour_id)
    if hour is None and hour_id is not None:
        return await bells_menu(uow, user_id)

    await state.set_state(BellsStatesGroup.create_or_update_bells)
    await state.update_data(hour_id=hour_id)

    web_app_button = KeyboardButton(
        text="Открыть редактор расписания",
        web_app=WebAppInfo(url=str(
            URL(settings.URL)
            .joinpath("tg-webapp", "bells")
            .update_query(**(
                {
                    'bells': json.dumps(hour.hours),
                    'months': json.dumps(hour.months),
                    'weekdays': json.dumps(hour.weekdays)
                } if hour else {'none': 'none'}
            ))
        ))
    )

    return MessageModel(
        text="Откройте редактор по кнопке ниже и измените расписание",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [web_app_button],
                [KeyboardButton(text="Отмена", icon_custom_emoji_id="5467864676320681402")]
            ],
            resize_keyboard=True
        )
    )


@router.callback_query(F.data == "add_school_bell")
async def _add_school_bell(callback_query: CallbackQuery, state: FSMContext):
    """Добавление нового звонкового расписания"""

    async with uow_factory() as uow:
        answer = await create_or_edit_bell(uow, callback_query.from_user.id, state)

        await callback_query.message.delete()
        await callback_query.message.answer(**answer)


@router.message(BellsStatesGroup.create_or_update_bells)
async def _create_or_edit_bells(message: Message, state: FSMContext):
    """Получение данных из редактора"""

    async with uow_factory() as uow:
        school_admin = await check_school_admin(message.from_user.id, uow.school_admin_repository, check_auth=True)

        if message.text == "Отмена":
            data = await state.get_data()
            hour_id: Optional[int] = data.get('hour_id') and int(data['hour_id'])

            await state.clear()

            if hour_id is None:
                answer = await bells_menu(uow, message.from_user.id)
            else:
                answer = await bell_menu(uow, message.from_user.id, hour_id)

            await (await message.answer('.', reply_markup=ReplyKeyboardRemove())).delete()
            await message.answer(**answer)
            return

        if message.content_type != ContentType.WEB_APP_DATA:
            await message.answer("Откройте редактор по кнопке ниже или отмените операцию")
            return

        data = await state.get_data()
        hour_id: Optional[int] = data.get('hour_id') and int(data['hour_id'])

        try:
            input_data: InputBellsWebAppDataType = json.loads(message.web_app_data.data)
            set_months = set(input_data['months'])
            set_weekdays = set(input_data['weekdays'])
            bells = input_data['bells']
        except (KeyError, TypeError, json.decoder.JSONDecodeError):
            await message.answer("Произошла ошибка при получении данных от редактора, попробуйте еще раз")
            return

        if not set_months or not set_weekdays:
            await message.answer("Расписание должно быть привязано к хотя бы одному месяцу и дню недели, попробуйте еще раз")
            return

        if len(bells) > 20:
            await message.answer("Расписание слишком длинное, попробуйте еще раз")
            return

        bells.sort(key=lambda b: time.fromisoformat(b['start']))

        time_format = re.compile(r'\d\d:\d\d')
        for i, bell in enumerate(bells):
            if not re.fullmatch(time_format, bell['start']) or not re.fullmatch(time_format, bell['end']):
                await message.answer("Произошла ошибка при получении данных от редактора, попробуйте еще раз")
                return

            if i != 0:
                if time.fromisoformat(bells[i-1]['end']) >= time.fromisoformat(bell['start']):
                    await message.answer("Следующий урок должен начинаться позже окончания предыдущего, попробуйте еще раз")
                    return

            if time.fromisoformat(bell['start']) >= time.fromisoformat(bell['end']):
                await message.answer("Время начала должно быть раньше времени окончания, попробуйте еще раз")
                return

        school_hours = await uow.hour_repository.get_school_hours(school_admin.dnevnik_admin.school_id)
        for school_hour in school_hours:
            if school_hour.hour_id != hour_id and set(school_hour.months) & set_months and set(school_hour.weekdays) & set_weekdays:
                await message.answer("У нового расписания есть пересечение с другими, попробуйте еще раз")
                return

        await state.clear()

        if bells:
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

        answer = await bells_menu(uow, message.from_user.id)

        await (await message.answer('.', reply_markup=ReplyKeyboardRemove())).delete()
        await message.answer(**answer)


@router.callback_query(F.data.startswith("delete_school_bell|"))
async def _delete_school_bell(callback_query: CallbackQuery):
    """Удаление звонкового расписания"""

    hour_id: Optional[int] = int(callback_query.data.split("|")[1])

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository, check_auth=True)

        await uow.hour_repository.delete_school_hour(school_admin.dnevnik_admin.school_id, hour_id)

        answer = await bells_menu(uow, callback_query.from_user.id)
        await callback_query.message.edit_text(**answer)
