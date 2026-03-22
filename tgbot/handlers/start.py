from aiogram import Router

from aiogram.types import Message
from aiogram.filters import CommandStart

from ..config import settings


__all__ = ['router']

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет! {settings.URL}")
