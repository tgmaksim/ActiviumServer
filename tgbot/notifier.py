from .bot import get_bot
from src.config.project_config import settings


__all__ = ['send_admin_message']


async def send_admin_message(message: str, **kwargs):
    bot = get_bot()

    messages = []
    for admin in settings.ADMIN_CHAT_IDS:
        messages.append(await bot.send_message(admin, message, **kwargs))

    return messages
