from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart

from .service import MenuService
from ...callbacks.menu import CallbackMenu
from ...utils.messages import send_service_result
from ...dependencies.services import ModuleService

from ...enums.modules import ModuleList
from ...enums.commands import CommandList


__all__ = ['router']

router = Router(name=ModuleList.menu)


@router.message(Command(CommandList.menu), ModuleService(MenuService))
async def _cmd_menu(message: Message, state: FSMContext, service: MenuService):
    """Открытие меню администратора образовательной организации"""

    await state.clear()

    answer = await service.menu(message.from_user.id)
    await send_service_result(message, answer)


@router.callback_query(CallbackMenu.filter(), ModuleService(MenuService))
async def _callback_menu(callback_query: CallbackQuery, state: FSMContext, service: MenuService):
    """Открытие меню кнопкой Назад"""

    await state.clear()

    answer = service.admin_menu()
    await send_service_result(callback_query, answer)


@router.message(CommandStart(deep_link=True, magic=F.args == "menu"), ModuleService(MenuService))
async def _start_with_menu(message: Message, state: FSMContext, service: MenuService):
    """Открытие меню после авторизации администратора образовательной организации"""

    await state.clear()

    answer = service.admin_menu()
    await send_service_result(message, answer)
