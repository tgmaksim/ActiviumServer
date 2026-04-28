import traceback

from typing import Optional

from http import HTTPStatus
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.log_service import LogService
from ..dependencies.uow import get_log_uow_factory


__all__ = ['LoggingMiddleware']


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования ошибок, результатов запросов и других данных"""

    async def dispatch(self, request: Request, call_next):
        error: Optional[str] = None
        response: Optional[Response] = None

        try:
            response = await call_next(request)
            error = getattr(request.state, 'error', None)
            return response
        except Exception as e:
            error = '\n'.join(traceback.format_exception(e))

            raise  # Ошибка доходит до последнего Middleware, который возвращает API-ответ
        finally:
            ip = request.headers.get('x-forwarded-for')
            session_id = getattr(request.state, 'session_id', None)
            value = (error
                     or (response and f"{response.status_code} {HTTPStatus(response.status_code).phrase}")
                     or "Error status")

            service = LogService(get_log_uow_factory())
            await service.log(
                ip=ip,
                path='?'.join(filter(None, (request.url.path, request.url.query))),  # Путь API-метода или страницы
                session_id=session_id,
                status=not bool(error),
                method=request.method,
                value=value
            )
