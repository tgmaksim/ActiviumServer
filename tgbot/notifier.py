from .bot import get_bot
from .config import settings


__all__ = ['send_admin_message']


async def send_admin_message(message: str, **kwargs):
    bot = get_bot()

    for admin in settings.ADMIN_CHAT_IDS:
        await bot.send_message(admin, message, **kwargs)
