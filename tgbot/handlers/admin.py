from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command

from hosting import reload_server

from ..config import settings


__all__ = ['router']

router = Router()


@router.message(Command('reload'))
async def _cmd_reload(message: Message):
    if message.from_user.id not in settings.ADMIN_CHAT_IDS:
        await message.answer("Данная команда доступна только администраторам")
        return

    try:
        response = await reload_server()
        state = response['state']
    except Exception:
        await message.answer("Произошла ошибка при перезагрузке")
        raise
    else:
        await message.answer(f"Activium перезагружается ({state})")
