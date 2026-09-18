from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from .service import SchoolEAService
from .states import ExtracurricularActivitiesStatesGroup

from src.models.school_admin_model import SchoolAdmin

from ...enums.modules import ModuleList
from ...utils.messages import send_service_result
from ...dependencies.services import ModuleService
from ...callbacks.school_ea import CallbackSchoolEA


__all__ = ['router']

router = Router(name=ModuleList.school_posts)


@router.callback_query(CallbackSchoolEA.filter_action('menu'), ModuleService(SchoolEAService), flags={'auth': True})
async def _ea_menu(callback_query: CallbackQuery, service: SchoolEAService):
    """Меню внеурочных занятий"""

    answer = await service.menu()
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolEA.filter_action('list_ea'), ModuleService(SchoolEAService), flags={'full_auth': True})
async def _list_ea(callback_query: CallbackQuery, params: dict, service: SchoolEAService, school_admin: SchoolAdmin):
    """Список внеурочных занятий"""

    answer = await service.list_ea(school_admin, params)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolEA.filter_action('delete'), ModuleService(SchoolEAService), flags={'auth': True})
async def _delete(callback_query: CallbackQuery, params: dict, service: SchoolEAService):
    """Удаление внеурочных занятий"""

    answer = await service.delete(params)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolEA.filter_action('confirm_delete'), ModuleService(SchoolEAService), flags={'full_auth': True})
async def _confirm_delete(callback_query: CallbackQuery, params: dict, service: SchoolEAService, school_admin: SchoolAdmin):
    """Подтверждение удаления внеурочных занятий"""

    answer = await service.confirm_delete(school_admin, params)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolEA.filter_action('add'), flags={'auth': True})
async def _add_ea(callback_query: CallbackQuery):
    """Добавление внеурочных занятий"""

    await callback_query.answer("Данная функция в разработке", show_alert=True)


@router.callback_query(CallbackSchoolEA.filter_action('edit'), ModuleService(SchoolEAService), flags={'auth': True})
async def _edit_ea(callback_query: CallbackQuery, state: FSMContext, params: dict, service: SchoolEAService, school_admin: SchoolAdmin):
    """Редактирование внеурочного занятия"""

    answer = await service.edit_ea(school_admin, params)
    await send_service_result(callback_query, answer)

    await state.set_state(ExtracurricularActivitiesStatesGroup.update_extracurricular_activity)
    await state.update_data(ea_id=params['ea_id'])


@router.message(ExtracurricularActivitiesStatesGroup.update_extracurricular_activity, F.text == "Отмена", ModuleService(SchoolEAService), flags={'auth': True})
async def _cancel_edit_ea(message: Message, state: FSMContext, service: SchoolEAService):
    """Отмена редактирования внеурочного занятия"""

    await state.clear()

    answer = await service.cancel_edit_ea()
    await send_service_result(message, answer)


@router.message(ExtracurricularActivitiesStatesGroup.update_extracurricular_activity, ModuleService(SchoolEAService), flags={'full_auth': True})
async def _update_ea(message: Message, state: FSMContext, service: SchoolEAService, school_admin: SchoolAdmin):
    """Получение данных от редактора для изменения внеурочного занятия"""

    ea_id = (await state.get_data())['ea_id']

    if message.content_type != ContentType.WEB_APP_DATA:
        await message.answer("Откройте редактор по кнопке ниже или отмените операцию")
        return

    answer = await service.update_ea(school_admin, ea_id, message.web_app_data.data)
    await send_service_result(message, answer)

    await state.clear()
