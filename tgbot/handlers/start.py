from aiogram import Router, F

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart


__all__ = ['router']

router = Router()


start_text = ("Здравствуйте!\n"
              "Данный бот предназначен для подключения образовательных организаций к сервису Активиум\n\n"
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


@router.message(F.text == "Отмена")
async def _message_start(message: Message):
    await message.answer(start_text, reply_markup=ReplyKeyboardRemove())
