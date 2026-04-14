from aiogram import Router

from aiogram.types import Message
from aiogram.filters import CommandStart


__all__ = ['router']

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет! Данный бот предназначен для подключения образовательных организаций к сервису Активиум. "
                         f"Данный функционал находится пока что в разработке\n"
                         f"Скачать можно по команде: /app")
