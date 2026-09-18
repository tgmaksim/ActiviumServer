from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command

from hosting import reload_server

from ...enums.modules import ModuleList
from ...enums.commands import CommandList
from src.config.project_config import settings

from .dependencies import AdminFilter


__all__ = ['router']

router = Router(name=ModuleList.admin)
router.message.filter(AdminFilter())


@router.message(Command(CommandList.reload))
async def _cmd_reload(message: Message):
    """Перезагрузка сервера по команде админа"""

    try:
        await reload_server()
    except Exception:
        await message.answer("Произошла ошибка при перезагрузке")
        raise
    else:
        await message.answer(f"{settings.PROJECT_NAME} перезагружается")
