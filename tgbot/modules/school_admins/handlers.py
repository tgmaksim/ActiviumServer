from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from aiogram.enums import ContentType
from aiogram.utils.formatting import Text

from .buttons import add_admin_buttons
from .states import AddMyAdminsStatesGroup
from ...utils.messages import send_service_result

from .service import MyAdminsService
from ...enums.modules import ModuleList
from ...dependencies.services import ModuleService
from ...callbacks.school_admins import CallbackSchoolAdmins


__all__ = ['router']

router = Router(name=ModuleList.school_admins)


@router.callback_query(CallbackSchoolAdmins.filter_action('menu'), ModuleService(MyAdminsService), flags={'auth': True})
async def _menu_my_admins(callback_query: CallbackQuery, service: MyAdminsService):
    """Список дочерних администраторов образовательной организации"""

    answer = await service.my_admins(callback_query.from_user.id)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolAdmins.filter_action('add'), ModuleService(MyAdminsService), flags={'auth': True})
async def _query_add_my_admins(callback_query: CallbackQuery, state: FSMContext):
    """Добавление дочернего администратора образовательной организации"""

    text = Text(
        "Отправьте пользователя (или несколько), которому будет выдано разрешение на администрирование"
    )
    reply_markup = add_admin_buttons()

    await callback_query.message.answer(**text.as_kwargs(), reply_markup=reply_markup)
    await callback_query.message.delete()

    await state.set_state(AddMyAdminsStatesGroup.users_shared)


@router.message(AddMyAdminsStatesGroup.users_shared, ModuleService(MyAdminsService), flags={'auth': True})
async def _add_my_admins(message: Message, service: MyAdminsService, state: FSMContext):
    """Ожидание сообщения с администратором(-ами) образовательной организации"""

    if message.content_type != ContentType.USERS_SHARED and message.text != "Отмена":
        await message.answer("Пришлите администратором кнопкой")
        return

    if message.content_type == ContentType.USERS_SHARED:
        new_my_admins = [
            (
                user.user_id,
                ' '.join([user.first_name, user.last_name or '']).strip()
            )
            for user in message.users_shared.users
        ]

        answer = await service.add_my_admins(message.from_user.id, new_my_admins)
        await send_service_result(message, answer)

    answer = await service.my_admins(message.from_user.id)
    await send_service_result(message, answer)

    await state.clear()


@router.callback_query(CallbackSchoolAdmins.filter_action('delete'), ModuleService(MyAdminsService), flags={'auth': True})
async def _delete_my_admin(callback_query: CallbackQuery, service: MyAdminsService, callback_data: CallbackSchoolAdmins):
    """Удаление дочернего администратора образовательной организации"""

    await service.delete_my_admin(callback_query.from_user.id, callback_data.user_id)

    answer = await service.my_admins(callback_query.from_user.id)
    await send_service_result(callback_query, answer)
