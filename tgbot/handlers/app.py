from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command

from ..config import settings


__all__ = ['router']

router = Router()


@router.message(Command('app'))
async def cmd_app(message: Message):
    await message.answer(f"Скачать здесь: {settings.URL}\n"
                         f"Исходный код: {settings.GITHUB}")
