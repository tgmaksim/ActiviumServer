from aiogram import Router, F

from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery


__all__ = ['router']

router = Router()


start_text = ("Здравствуйте! <tg-emoji emoji-id=\"5343984088493599366\">👋</tg-emoji>\n"
              "Данный бот предназначен для подключения образовательных организаций к сервису "
              "Активиум <tg-emoji emoji-id=\"5406575351272872039\">🤓</tg-emoji>\n\n"
              "Подключить ОО: /school\n"
              "Меню администратора: /menu\n"
              "Скачать можно по команде: /app\n"
              "Помощь: /help")


@router.message(CommandStart())
async def _cmd_start(message: Message):
    await message.answer(start_text)


@router.callback_query(F.data == "start")
async def _callback_start(callback_query: CallbackQuery):
    await callback_query.message.edit_text(start_text)
