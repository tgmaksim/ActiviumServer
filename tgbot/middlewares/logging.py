import traceback

from typing import Any, Dict, Callable, Awaitable, Optional

from aiogram.types import Update
from aiogram import BaseMiddleware

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory


__all__ = ['LoggingMiddleware']


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования всех событий с Telegram-ботом"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        error: Optional[str] = None

        try:
            result = await handler(event, data)
            return result

        except Exception as e:
            error = '\n'.join(traceback.format_exception(e))
            print(error)

            raise
        finally:
            await self._log_event(event, error)

    async def _log_event(self, event: Update, error: Optional[str]):
        ip = "tg"

        # Получение идентификатор пользователя или чата
        entity = (getattr(event.message, 'from_user', None) or getattr(event.message, 'chat', None) or
                  getattr(event.callback_query, 'from_user', None) or
                  getattr(getattr(event.callback_query, 'message', None), 'from_user', None) or
                  getattr(getattr(event.callback_query, 'message', None), 'chat', None))
        session_id = getattr(entity, 'id', None)

        path = self._extract_path(event)

        value = error or "OK"
        if not error and event.event_type not in ('message', 'edited_message', 'callback_query'):
            value = event.model_dump_json()  # Если нет ошибки, но событие нестандартное, то выводится полная информация о нем

        # Логирование события и добавление статистики
        service = LogService(get_log_uow_factory())
        await service.log(
            ip=ip,
            path=path,
            session_id=str(session_id) if session_id else None,
            status=not bool(error),
            method=event.event_type,
            value=value,
        )
        await service.stat(None, f'{ip}_{event.event_type}')

    @staticmethod
    def _extract_path(event: Update) -> str:
        """Получение содержания события (текст сообщения, callback_data или сериализованный объект Update)"""

        if event.message and event.message.text:
            return event.message.text

        if event.callback_query and event.callback_query.data:
            return event.callback_query.data

        return event.model_dump_json()
