import itertools

from datetime import timedelta

from aiogram import Router, F

from dnevnikru import AioDnevnikruApi, DnevnikruApiException

from src.utils.zip_int import zip_int, unzip_int

from src.utils.datetime import datetime_now, astimezone
from src.dependencies.httpx import get_httpx_client
from src.dependencies.uow import get_app_uow_factory

from ..utils.auth import check_school_admin
from ..utils.messages import secure_edit_message
from aiogram.utils.formatting import Text, CustomEmoji

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


__all__ = ['router']

router = Router()

uow_factory = get_app_uow_factory()

SHOWN_EA_LIMIT = 7

# TODO: показать внеурочки за 32 дня назад и неограниченно вперед (почти работает)
# TODO: удалить все внеурочки (показанные)
# TODO: изменить данные внеурочки
# TODO: добавить внеурочки (с копированием на несколько дней) через Telegram Web Mini App


@router.callback_query(F.data == "school_ea")
async def _school_ea(callback_query: CallbackQuery):
    """Внеурочные занятия в образовательной организации"""

    async with uow_factory() as uow:
        await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)

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

        await callback_query.message.edit_text(**text.as_kwargs(), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data.startswith("lea|m|"))
async def _school_extracurricular_activity_menu(callback_query: CallbackQuery):
    await callback_query.answer("В разработке", show_alert=True)


@router.callback_query(F.data.startswith("lea|"))
async def _school_extracurricular_activities(callback_query: CallbackQuery):
    """Список доступных внеурочных занятий в образовательной организации"""

    level, offset, *params = callback_query.data.split("|")[1:]
    offset: int = int(offset)

    levels = ["g", "sp", "ea", "m"]  # group, subject_place, extracurricular_activity, menu
    next_level = levels[levels.index(level) + 1]
    previous_level = levels[levels.index(level) - 1] if levels.index(level) - 1 >= 0 else None

    async with uow_factory() as uow:
        school_admin = await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)
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

            try:
                group = await dnr.get_group(group_id)
                group_name = group['fullName']
            except DnevnikruApiException:
                await callback_query.answer("Не удалось получить данные группы от Дневника.ру", show_alert=True)
                raise

            subjects_places = await (
                uow.extracurricular_activity_repository
                .get_subject_place_by_group(
                    school_admin.dnevnik_admin.school_id, group_id, since, offset,
                    limit=SHOWN_EA_LIMIT + 1  # Для проверки существования следующего предмета с кабинетом после лимита
                )
            )

            entities = [(str(i), f"{subject} - {place}") for i, (subject, place) in enumerate(subjects_places)]
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

            try:
                group = await dnr.get_group(group_id)
                group_name = group['fullName']
            except DnevnikruApiException:
                await callback_query.answer("Не удалось получить данные группы от Дневника.ру", show_alert=True)
                raise

            extracurricular_activities = await (
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

        buttons.append([InlineKeyboardButton(text="Назад", callback_data=back_data, icon_custom_emoji_id="5467864676320681402")])

        text = Text(
            CustomEmoji("🏫", custom_emoji_id="5265002646397285605"), " ", level_text
        )

        await secure_edit_message(callback_query, **text.as_kwargs(), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
