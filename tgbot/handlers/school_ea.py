import json
import itertools

from yarl import URL
from asyncio import gather
from datetime import timedelta

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from dnevnikru import AioDnevnikruApi, DnevnikruApiException

from src.config.project_config import settings
from src.utils.zip_int import zip_int, unzip_int

from src.dependencies.httpx import get_httpx_client
from src.dependencies.uow import get_app_uow_factory
from src.utils.datetime import datetime_now, astimezone

from ..utils.auth import check_school_admin
from ..utils.message_model import MessageModel
from ..utils.messages import secure_edit_message
from aiogram.utils.formatting import Text, CustomEmoji

from aiogram.types import (
    WebAppInfo,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


__all__ = ['router']

router = Router()

uow_factory = get_app_uow_factory()

SHOWN_EA_LIMIT = 7


class ExtracurricularActivitiesStatesGroup(StatesGroup):
    """Группа состояний при изменении внеурочных занятий в образовательной организации"""

    update_extracurricular_activity = State('update_extracurricular_activity')
    """Ожидание сообщения от Web Mini App с данными об обновленном внеурочном занятии"""

    create_extracurricular_activities = State('create_extracurricular_activities')
    """Ожидание сообщения от Web Mini App с данными о созданных внеурочных занятиях"""


async def get_group_name(group_id: int, dnr: AioDnevnikruApi, callback_query: CallbackQuery) -> str:
    try:
        group = await dnr.get_group(group_id)
        group_name = group['fullName']
    except DnevnikruApiException:
        await callback_query.answer("Не удалось получить данные класса от Дневника.ру", show_alert=True)
        raise

    return group_name


@router.callback_query(F.data == "school_ea")
async def _school_ea(callback_query: CallbackQuery):
    """Внеурочные занятия в образовательной организации"""

    async with uow_factory() as uow:
        await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)

        answer = school_ea()

        await callback_query.message.edit_text(**answer)


def school_ea() -> MessageModel:
    text = Text(
        CustomEmoji("🏫", custom_emoji_id="5265002646397285605"), " ",
        "Внеурочные занятия в образовательной организации"
    )

    buttons = [
        [InlineKeyboardButton(text="Список внеурочных занятий", callback_data="lea|g|0", icon_custom_emoji_id="5265002646397285605")],
        [InlineKeyboardButton(text="Удалить все занятия", callback_data="delete_school_ea|all", icon_custom_emoji_id="5210952531676504517")],
        [InlineKeyboardButton(text="Добавить внеурочные занятия", callback_data="add_school_ea", icon_custom_emoji_id="5397916757333654639")],
        [InlineKeyboardButton(text="Назад", callback_data="menu", icon_custom_emoji_id="5467864676320681402")]
    ]

    return MessageModel(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("lea|m|"))
async def _school_extracurricular_activity_menu(callback_query: CallbackQuery):
    """Меню конкретного внеурочного занятия в образовательной организации"""

    group_id, _i, ea_id = map(unzip_int, callback_query.data.split("|")[3:])

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository,
                                                check_auth=True)
        dnr = AioDnevnikruApi(get_httpx_client(), school_admin.dnevnik_admin.dnevnik_token)

        group_name, extracurricular_activity = await gather(
            get_group_name(group_id, dnr, callback_query),
            uow.extracurricular_activity_repository
            .get_extracurricular_activity(school_admin.dnevnik_admin.school_id, ea_id)
        )

        if extracurricular_activity is None:
            await callback_query.answer("Внеурочное занятие не найдено. Обновите список", show_alert=True)
            return

        text = Text(
            CustomEmoji("🏫", custom_emoji_id="5265002646397285605"), " ",
            f"Внеурочное занятие у {group_name} {extracurricular_activity.start_time.strftime('%e %b.')}"
            f" ({extracurricular_activity.hours['string']})\n",
            extracurricular_activity.subject, "\n",
            extracurricular_activity.place
        )

        buttons = [
            [InlineKeyboardButton(text="Изменить данные", callback_data=f"edit_ea|{zip_int(ea_id)}", icon_custom_emoji_id="5395444784611480792")],
            [InlineKeyboardButton(text="Удалить внеурочное занятие", callback_data=f"delete_ea|{zip_int(ea_id)}", style='danger', icon_custom_emoji_id="5210952531676504517")],
            [InlineKeyboardButton(text="Назад", callback_data=f"lea|ea|0|{zip_int(group_id)}|{zip_int(_i)}", icon_custom_emoji_id="5467864676320681402")]
        ]

        await callback_query.message.edit_text(**text.as_kwargs(), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("lea|"))
async def _school_extracurricular_activities(callback_query: CallbackQuery):
    """Список доступных внеурочных занятий в образовательной организации"""

    level, offset, *params = callback_query.data.split("|")[1:]
    offset: int = int(offset)

    levels = ["g", "sp", "ea", "m"]  # group, subject_place, extracurricular_activity, menu
    next_level = levels[levels.index(level) + 1]
    previous_level = levels[levels.index(level) - 1] if levels.index(level) - 1 >= 0 else None

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository, check_auth=True)
        dnr = AioDnevnikruApi(get_httpx_client(), school_admin.dnevnik_admin.dnevnik_token)

        since = datetime_now(school_admin.dnevnik_admin.timezone) - timedelta(days=32)

        entities: list[tuple[str, str]]
        level_text: Text
        back_data: str

        if level == "g":  # group
            groups_id = await (
                uow.extracurricular_activity_repository
                .get_groups(
                    school_admin.dnevnik_admin.school_id, since, offset,
                    limit=SHOWN_EA_LIMIT + 1  # Для проверки существования следующего класса после лимита
                )
            )
            groups = await dnr.get_groups(groups_id) if groups_id else []

            entities = [(zip_int(group['group']['id']), group['group']['fullName']) for group in groups]
            level_text = Text("Выберите учебную группу (класс), в котором проводятся внеурочные занятия")
            back_data = 'school_ea'

        elif level == "sp":  # subject_place
            group_id = unzip_int(params[0])

            group_name, subjects_places = await gather(
                get_group_name(group_id, dnr, callback_query),
                uow.extracurricular_activity_repository
                .get_subject_place_by_group(
                    school_admin.dnevnik_admin.school_id, group_id, since, offset,
                    limit=SHOWN_EA_LIMIT + 1  # Для проверки существования следующего предмета с кабинетом после лимита
                )
            )

            entities = [(zip_int(i), f"{subject} - {place}") for i, (subject, place) in enumerate(subjects_places)]
            level_text = Text(f"Выберите предмет и кабинет, в котором проводятся внеурочные занятия у {group_name}")
            back_data = f'lea|{previous_level}|0'

        elif level == "ea":  # extracurricular_activity
            group_id = unzip_int(params[0])

            if callback_query.message.text.count('\n') == 2:
                _, subject, place = callback_query.message.text.split('\n')
            else:
                inline_keyboard_matrix = callback_query.message.reply_markup.inline_keyboard
                inline_keyboard: list[InlineKeyboardButton] = list(itertools.chain.from_iterable(inline_keyboard_matrix))
                button_text = next(button.text for button in inline_keyboard if button.callback_data == callback_query.data)

                subject, place = button_text.split(' - ')

            group_name, extracurricular_activities = await gather(
                get_group_name(group_id, dnr, callback_query),
                uow.extracurricular_activity_repository
                .get_extracurricular_activities_by_subject_place(
                    school_admin.dnevnik_admin.school_id, group_id, subject, place, since, offset,
                    limit=SHOWN_EA_LIMIT + 1  # Для проверки существования следующего внеурочного занятия после лимита
                )
            )

            entities = [(
                zip_int(ea.ea_id),
                astimezone(ea.start_time, school_admin.dnevnik_admin.timezone).strftime('%e %b. в %H:%M')
            ) for ea in extracurricular_activities]
            level_text = Text(f"Выберите время проведения внеурочного занятия у {group_name}\n{subject}\n{place}")
            back_data = f'lea|{previous_level}|0|{zip_int(group_id)}'

        else:
            raise RuntimeError(f"level is '{level}'")

        # Переход на следующий уровень
        suffix_callback_data = ''.join(f"|{param}" for param in params)
        buttons = [[InlineKeyboardButton(
            text=entity_name,
            callback_data=f"lea|{next_level}|0{suffix_callback_data}|{entity_id}"
        )] for i, (entity_id, entity_name) in enumerate(entities) if i < SHOWN_EA_LIMIT]

        right_offset = offset + SHOWN_EA_LIMIT
        left_offset = max(0, offset - SHOWN_EA_LIMIT)

        # Кнопки влево, обновить, вправо для перемещения по списку
        buttons.append([
            InlineKeyboardButton(text=" ", icon_custom_emoji_id="5877536313623711363" if left_offset != offset else None,
                                 callback_data=f"lea|{level}|{left_offset}{suffix_callback_data}"),
            InlineKeyboardButton(text=" ", icon_custom_emoji_id="5030872266716480568",
                                 callback_data=f"lea|{level}|{offset}{suffix_callback_data}"),
            InlineKeyboardButton(text=" ", icon_custom_emoji_id="5875506366050734240" if len(entities) > SHOWN_EA_LIMIT else None,
                                 callback_data=f"lea|{level}|{right_offset}{suffix_callback_data}")
        ])

        if level == 'ea':
            buttons.append([InlineKeyboardButton(text="Удалить все", callback_data=f"del_ea{suffix_callback_data}",
                                                 icon_custom_emoji_id="5210952531676504517")])

        buttons.append([InlineKeyboardButton(text="Назад", callback_data=back_data, icon_custom_emoji_id="5467864676320681402")])

        text = Text(
            CustomEmoji("🏫", custom_emoji_id="5265002646397285605"), " ", level_text
        )

        await secure_edit_message(callback_query, **text.as_kwargs(), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data == "delete_school_ea|all|confirm")
async def _delete_all_school_ea_confirm(callback_query: CallbackQuery):
    """Удаление всех внеурочных занятий в образовательной организации"""

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository, check_auth=True)

        await uow.extracurricular_activity_repository.delete_all_school(school_admin.dnevnik_admin.school_id)

        answer = school_ea()
        await callback_query.message.edit_text(**answer)


@router.callback_query(F.data == "delete_school_ea|all")
async def _delete_all_school_ea(callback_query: CallbackQuery):
    """Подтверждение удаления всех внеурочных занятий в образовательной организации"""

    async with uow_factory() as uow:
        await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)

        text = Text(
            CustomEmoji("❓", custom_emoji_id="5452069934089641166"), " ",
            "Вы уверены, что хотите удалить ВСЕ внеурочные занятия?"
        )

        buttons = [
            [InlineKeyboardButton(text="Да, удалить", callback_data=f"{callback_query.data}|confirm",
                                  style='danger', icon_custom_emoji_id="5210952531676504517")],
            [InlineKeyboardButton(text="Назад", callback_data="school_ea", icon_custom_emoji_id="5467864676320681402")]
        ]

        await callback_query.message.edit_text(**text.as_kwargs(), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("del_ea|confirm|"))
async def _del_ea_confirm(callback_query: CallbackQuery):
    """Удаление группы внеурочных занятий"""

    group_id = unzip_int(callback_query.data.split('|')[2])
    subject, place = callback_query.message.text.split('\n')[1:]

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository, check_auth=True)

        await uow.extracurricular_activity_repository.delete_extracurricular_activities_by_subject_place(
            school_admin.dnevnik_admin.school_id, group_id, subject, place
        )

        answer = school_ea()
        await callback_query.message.edit_text(**answer)


@router.callback_query(F.data.startswith("del_ea|"))
async def _del_ea(callback_query: CallbackQuery):
    """Подтверждение удаления группы внеурочных занятий"""

    group_id, _i = map(unzip_int, callback_query.data.split('|')[1:])
    subject, place = callback_query.message.text.split('\n')[1:]

    async with uow_factory() as uow:
        await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)

        text = Text(
            CustomEmoji("❓", custom_emoji_id="5452069934089641166"), " ",
            "Вы уверены, что хотите удалить все внеурочные занятия?\n",
            subject, "\n",
            place
        )

        buttons = [
            [InlineKeyboardButton(text="Да, удалить", callback_data=f"del_ea|confirm|{zip_int(group_id)}",
                                  style='danger', icon_custom_emoji_id="5210952531676504517")],
            [InlineKeyboardButton(text="Назад", callback_data=f"lea|ea|0|{zip_int(group_id)}|{zip_int(_i)}", icon_custom_emoji_id="5467864676320681402")]
        ]

        await callback_query.message.edit_text(**text.as_kwargs(), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("delete_ea|"))
async def _delete_ea(callback_query: CallbackQuery):
    """Удаление конкретного внеурочного занятия"""

    ea_id = unzip_int(callback_query.data.split('|')[1])

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository, check_auth=True)

        await uow.extracurricular_activity_repository.delete_extracurricular_activity(school_admin.dnevnik_admin.school_id, ea_id)

        answer = school_ea()
        await callback_query.message.edit_text(**answer)


@router.callback_query(F.data == "add_school_ea")
async def _add_school_ea(callback_query: CallbackQuery, state: FSMContext):
    """Добавление внеурочного(ых) занятия(ий) с помощью Web Mini App"""

    await callback_query.answer("Данная функция в разработке", show_alert=True)

    # async with uow_factory() as uow:
    #     school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository, check_auth=True)
    #     dnr = AioDnevnikruApi(get_httpx_client(), school_admin.dnevnik_admin.dnevnik_token)
    #
    #     await state.set_state(ExtracurricularActivitiesStatesGroup.create_extracurricular_activities)
    #
    #     web_app = WebAppInfo(url=str(
    #         URL(settings.URL)
    #         .joinpath("tg-webapp", "extracurricular_activity")
    #         .update_query(
    #             groups=json.dumps()
    #         )
    #     ))


@router.callback_query(F.data.startswith("edit_ea|"))
async def _edit_extracurricular_activity(callback_query: CallbackQuery, state: FSMContext):
    """Редактирование данных внеурочного занятия"""

    await callback_query.answer("Данная функция в разработке", show_alert=True)

    # ea_id = unzip_int(callback_query.data.split("|")[1])
    #
    # async with uow_factory() as uow:
    #     school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)
    #
    #     extracurricular_activity = await (
    #         uow.extracurricular_activity_repository
    #         .get_extracurricular_activity(school_admin.dnevnik_admin.school_id, ea_id)
    #     )
    #
    #     if extracurricular_activity is None:
    #         await callback_query.answer("Внеурочное занятие не найдено! Вернитесь назад", show_alert=True)
    #         return
    #
    #     await state.set_state(ExtracurricularActivitiesStatesGroup.update_extracurricular_activity)
    #     await state.update_data(ea_id=ea_id)
    #
    #     web_app = WebAppInfo(url=str(
    #         URL(settings.URL)
    #         .joinpath("tg-webapp", "extracurricular_activity")
    #         .update_query(
    #             subject=extracurricular_activity.subject,
    #             place=extracurricular_activity.place,
    #             hours=json.dumps(extracurricular_activity.hours)
    #         )
    #     ))
