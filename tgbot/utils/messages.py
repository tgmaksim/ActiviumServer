from typing import Union

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from ..schemas.service_result import ServiceResult


__all__ = ['secure_edit_message', 'send_service_result']


async def secure_edit_message(callback_query: CallbackQuery, **kwargs):
    """Изменить сообщения или в случе ошибки 'message is not modified' вызвать answer()"""

    try:
        await callback_query.message.edit_text(**kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in e.message:
            await callback_query.answer()
        else:
            raise


async def send_service_result(event: Union[Message, CallbackQuery], answer: ServiceResult):
    """Отправка результата обработки запроса пользователю"""

    if isinstance(event, Message):
        if answer.service_params.delete_keyboard:
            await (await event.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

        if answer.service_params.delete_message:
            await event.delete()

        if answer.text is not None:
            await event.answer(**answer)

    else:
        if answer.service_params.delete_keyboard:
            await (await event.message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

        if answer.service_params.delete_message:
            await event.message.delete()

        if answer.alert is not None:
            await event.answer(answer.alert, show_alert=True)

        if answer.text is not None:
            if answer.service_params.delete_message:
                await event.message.answer(**answer)
            else:
                await secure_edit_message(event, **answer)
