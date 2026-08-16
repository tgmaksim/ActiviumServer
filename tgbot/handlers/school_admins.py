from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ..utils.auth import check_school_admin
from ..utils.message_model import MessageModel
from aiogram.utils.formatting import Text, CustomEmoji

from src.dependencies.uow import get_app_uow_factory
from src.repositories.statistic_repository import StatName

from src.support.repositories.app_uow import AppUnitOfWork

from aiogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButtonRequestUsers,
)


__all__ = ['router']

router = Router()

uow_factory = get_app_uow_factory()

MY_ADMINS_LIMIT = 5  # Лимит дочерних администраторов образовательной организации


class AddMyAdminsStatesGroup(StatesGroup):
    """Группа состояний при добавлении дочернего администратора образовательной организации"""

    users_shared = State('users_shared')
    """Ожидание сообщения с пользователями"""


@router.callback_query(F.data == "my_admins")
async def _my_admins(callback_query: CallbackQuery):
    """Список дочерних администраторов образовательной организации"""

    async with uow_factory() as uow:
        answer = await menu_my_admins(uow, callback_query.from_user.id)
        await callback_query.message.edit_text(**answer)


async def menu_my_admins(uow: AppUnitOfWork, user_id: int) -> MessageModel:
    """Список дочерних администраторов образовательной организации"""

    await check_school_admin(user_id, uow.school_admin_repository)

    # Дочерние администраторы образовательной организации
    my_admins = await uow.school_admin_repository.get_my_admins(user_id)

    # Кнопки для удаления дочерних администраторов образовательной организации
    buttons = [[InlineKeyboardButton(
        text=admin.name,
        icon_custom_emoji_id="5210952531676504517",
        style='danger',
        callback_data=f"delete_my_admin|{admin.user_id}"
    )] for admin in my_admins]

    buttons.append([InlineKeyboardButton(text="Добавить администратора", icon_custom_emoji_id="5397916757333654639", callback_data="add_admin")])
    buttons.append([InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="menu")])

    return MessageModel(
        text=Text(CustomEmoji("✅", custom_emoji_id="5440712623219822019"), " Мои администраторы"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "add_admin")
async def _query_add_admin(callback_query: CallbackQuery, state: FSMContext):
    """Добавление дочернего администратора образовательной организации"""

    async with uow_factory() as uow:
        await check_school_admin(callback_query.from_user.id, uow.school_admin_repository)

        await callback_query.message.answer(
            "Отправьте пользователя (или несколько), которому будет выдано разрешение на администрирование",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Выбрать пользователя(ей)", request_users=KeyboardButtonRequestUsers(
                        request_id=0, user_is_bot=False, request_name=True, max_quantity=10))],
                    [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]
                ],
                is_persistent=True, resize_keyboard=True, input_field_placeholder="Выберите кнопкой")
        )
        await callback_query.message.delete()

        await state.set_state(AddMyAdminsStatesGroup.users_shared)


@router.message(AddMyAdminsStatesGroup.users_shared)
async def _add_admin(message: Message, state: FSMContext):
    """Ожидание сообщения с администратором(-ами) образовательной организации"""

    async with uow_factory() as uow:
        await check_school_admin(message.from_user.id, uow.school_admin_repository)

        if message.content_type != ContentType.USERS_SHARED and message.text != "Отмена":
            await message.answer("Пришлите администратором кнопкой")
            return

        await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

        if message.content_type == ContentType.USERS_SHARED:
            users = [(
                user.user_id,
                ' '.join([user.first_name, user.last_name or '']).strip()
            ) for user in message.users_shared.users]
            my_admins = await uow.school_admin_repository.get_my_admins(message.from_user.id)

            if len(my_admins) + len(users) > MY_ADMINS_LIMIT:
                await message.answer(f"Превышен лимит администраторов ({MY_ADMINS_LIMIT})")
            else:
                await uow.school_admin_repository.add_my_admins(message.from_user.id, users)

                await uow.statistic_repository.add_statistic(message.from_user.id, StatName.addSchoolAdminFrom)

        answer = await menu_my_admins(uow, message.from_user.id)
        await message.answer(**answer)

        await state.clear()


@router.callback_query(F.data.startswith("delete_my_admin|"))
async def _delete_admin(callback_query: CallbackQuery):
    """Удаление дочернего администратора образовательной организации"""

    admin_id = int(callback_query.data.split("|")[1])
    user_id = callback_query.from_user.id

    async with uow_factory() as uow:
        await check_school_admin(user_id, uow.school_admin_repository)

        await uow.school_admin_repository.delete_my_admin(user_id, admin_id)

        await uow.statistic_repository.add_statistic(user_id, StatName.deleteSchoolAdminFrom)

        answer = await menu_my_admins(uow, user_id)
        await callback_query.message.edit_text(**answer)
