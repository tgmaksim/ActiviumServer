from typing import Any, Dict, Callable, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.utils.formatting import Text
from aiogram.types import Message, CallbackQuery

from aiogram.dispatcher.flags import get_flag

from src.dependencies.uow import get_app_uow_factory
from ..dependencies.school_admin import get_school_admin

from src.config.project_config import settings

from ..enums.commands import CommandList


__all__ = ['AuthMiddleware']


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации администратора образовательной организации"""

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        uow_factory = get_app_uow_factory()
        answer: Callable[[...], Awaitable[Any]]

        if isinstance(event, Message):
            answer = event.answer
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            answer = event.message.edit_text
            user_id = event.from_user.id
        else:
            return None

        auth = get_flag(data, 'auth') is True
        full_auth = get_flag(data, 'full_auth') is True

        if not auth and not full_auth:
            return await handler(event, data)

        async with uow_factory() as uow:
            school_admin = await get_school_admin(user_id, uow.school_admin_repository, check_auth=full_auth)

        if school_admin is not None:
            data['school_admin'] = school_admin
            return await handler(event, data)

        text = Text(
            f"Меню {settings.PROJECT_NAME_RU} доступно только администраторам ОО. "
            "Возможно, Ваша сессия истекла\n\n"
            f"Для подключения: /{CommandList.school}\n"
            f"Для продления: /{CommandList.menu}"
        )

        async with uow_factory() as uow:
            await uow.school_admin_repository.kill_admin(user_id)

        await answer(**text.as_kwargs())

        return None
