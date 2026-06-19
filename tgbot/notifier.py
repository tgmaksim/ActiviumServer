from asyncio import gather

from aiogram.types import Message

from .config.bot import get_bot

from src.config.project_config import settings


__all__ = ['send_admin_message']


async def send_admin_message(message: str, **kwargs) -> list[Message]:
    """
    Отправка сообщения всех админам

    :param message: текстовое сообщение с форматированием html по умолчанию
    :param kwargs: дополнительные параметры для ``Bot.send_message()``
    :return: список сообщений, отправленных админам
    """

    bot = get_bot()

    messages: list[Message] = await gather(
        *(bot.send_message(admin, message, **kwargs) for admin in settings.ADMIN_CHAT_IDS)
    )

    return messages
