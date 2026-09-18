from aiogram.types import Message
from aiogram.filters import Filter

from src.config.project_config import settings


__all__ = ['AdminFilter']


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.ADMIN_CHAT_IDS
