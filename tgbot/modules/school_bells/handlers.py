from typing import Optional

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.models import SchoolAdmin

from ...enums.modules import ModuleList
from ...utils.messages import send_service_result
from ...dependencies.services import ModuleService
from ...callbacks.school_bells import CallbackSchoolBells

from .states import BellsStatesGroup
from .service import SchoolBellsService


__all__ = ['router']

router = Router(name=ModuleList.school_bells)


@router.callback_query(CallbackSchoolBells.filter_action('menu'), ModuleService(SchoolBellsService), flags={'auth': True})
async def _school_bells(callback_query: CallbackQuery, service: SchoolBellsService, school_admin: SchoolAdmin):
    """Список звонковых расписаний образовательной организации"""

    answer = await service.school_bells(school_admin)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolBells.filter_action('item'), ModuleService(SchoolBellsService), flags={'auth': True})
async def _school_bell(callback_query: CallbackQuery, callback_data: CallbackSchoolBells, service: SchoolBellsService, school_admin: SchoolAdmin):
    """Меню конкретного звонкового расписания"""

    answer = await service.school_bell(school_admin, callback_data.hour_id)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolBells.filter_action('edit'), ModuleService(SchoolBellsService), flags={'full_auth': True})
async def _edit_school_bell(callback_query: CallbackQuery, state: FSMContext, callback_data: CallbackSchoolBells, service: SchoolBellsService, school_admin: SchoolAdmin):
    """Редактирование звонкового расписания"""

    answer = await service.create_or_edit_school_bell(school_admin, callback_data.hour_id)
    await send_service_result(callback_query, answer)

    await state.set_state(BellsStatesGroup.create_or_edit_bell)
    await state.update_data(hour_id=callback_data.hour_id)


@router.callback_query(CallbackSchoolBells.filter_action('add'), ModuleService(SchoolBellsService), flags={'full_auth': True})
async def _add_school_bell(callback_query: CallbackQuery, state: FSMContext, service: SchoolBellsService, school_admin: SchoolAdmin):
    """Добавление звонкового расписания"""

    answer = await service.create_or_edit_school_bell(school_admin, None)
    await send_service_result(callback_query, answer)

    await state.set_state(BellsStatesGroup.create_or_edit_bell)
    await state.update_data(hour_id=None)


@router.message(BellsStatesGroup.create_or_edit_bell, F.text == "Отмена", ModuleService(SchoolBellsService), flags={'auth': True})
async def _cancel_create_or_edit_school_bell(message: Message, state: FSMContext, service: SchoolBellsService, school_admin: SchoolAdmin):
    """Отмена создания или изменения звонкового расписания"""

    data = await state.get_data()
    hour_id: Optional[int] = data.get('hour_id') and int(data['hour_id'])

    await state.clear()

    answer = await service.cancel_create_or_edit_bell(school_admin, hour_id)
    await send_service_result(message, answer)


@router.message(BellsStatesGroup.create_or_edit_bell, ModuleService(SchoolBellsService), flags={'full_auth': True})
async def _create_or_edit_school_bell(message: Message, state: FSMContext, service: SchoolBellsService, school_admin: SchoolAdmin):
    """Получение данных от редактора"""

    if message.content_type != ContentType.WEB_APP_DATA:
        await message.answer("Откройте редактор по кнопке ниже или отмените операцию")
        return

    data = await state.get_data()
    hour_id: Optional[int] = data.get('hour_id') and int(data['hour_id'])

    answer = await service.cancel_create_or_edit_bell(school_admin, hour_id)
    await send_service_result(message, answer)

    if answer.success:
        await state.clear()


@router.callback_query(CallbackSchoolBells.filter_action('delete'), ModuleService(SchoolBellsService), flags={'full_auth': True})
async def _delete_school_bell(callback_query: CallbackQuery, callback_data: CallbackSchoolBells, service: SchoolBellsService, school_admin: SchoolAdmin):
    """Удаление звонкового расписания"""

    answer = await service.delete_school_bell(school_admin, callback_data.hour_id)
    await send_service_result(callback_query, answer)
