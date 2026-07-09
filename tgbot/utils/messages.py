from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest


__all__ = ['secure_edit_message']


async def secure_edit_message(callback_query: CallbackQuery, **kwargs):
    """Изменить сообщения или в случе ошибки 'message is not modified' вызвать answer()"""

    try:
        await callback_query.message.edit_text(**kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in e.message:
            await callback_query.answer()
        else:
            raise
