from typing import Any, Dict, Callable, Awaitable

from aiogram.types import Update
from aiogram import BaseMiddleware

from src.dependencies.uow import get_app_uow_factory
from tgbot.utils.school_admin_error import SchoolAdminError

from src.config.project_config import settings


__all__ = ['ApiMiddleware']


class ApiMiddleware(BaseMiddleware):
    """Middleware для обработки ошибок API"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except SchoolAdminError as error:
            text = (f"Меню {settings.PROJECT_NAME_RU} доступно только администраторам ОО. "
                    "Возможно, Ваша сессия истекла\n\n"
                    "Для подключения: /school\n"
                    "Для продления: /menu")

            uow_factory = get_app_uow_factory()
            async with uow_factory() as uow:
                await uow.school_admin_repository.kill_admin(error.user_id)

            if event.event_type == "message":
                await event.message.answer(text)
            elif event.event_type == "callback_query":
                await event.callback_query.message.edit_text(text)

            raise
