from asyncio import gather
from typing import Optional, Union

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text
from aiogram.types import ReplyKeyboardMarkup, Message
from aiogram.client.default import DefaultBotProperties

from src.config.project_config import settings


__all__ = ['admin_notifier', 'AdminNotifier']


class AdminNotifier:
    def __init__(self):
        self._bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    async def send_to_admin(self, text: Union[Text, str], reply_markup: Optional[ReplyKeyboardMarkup] = None, **kwargs) -> list[Message]:
        t = text.as_kwargs() if isinstance(text, Text) else {'text': text}

        return await gather(
            *(self._bot.send_message(admin, **t, reply_markup=reply_markup, **kwargs) for admin in settings.ADMIN_CHAT_IDS)
        )

    async def close(self):
        await self._bot.session.close()


admin_notifier = AdminNotifier()
