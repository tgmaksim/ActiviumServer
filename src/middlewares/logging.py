import traceback

from typing import Optional

from fastapi.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.log_service import LogService
from ..dependencies.uow import get_log_uow_factory


__all__ = ['LoggingMiddleware']


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        error: Optional[str] = None

        try:
            response = await call_next(request)
            error = getattr(request.state, 'error', None)
            return response
        except Exception as e:
            error = '\n'.join(traceback.format_exception(e))

            raise
        finally:
            ip = request.headers.get('x-forwarded-for')
            session_id = getattr(request.state, 'session_id', None)

            service = LogService(get_log_uow_factory())
            await service.log(
                ip=ip,
                path=request.url.path,
                session_id=session_id,
                status=not bool(error),
                method=request.method,
                value=error or "200 OK"
            )
