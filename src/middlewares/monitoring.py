import time

from datetime import timedelta

from fastapi.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..dependencies.uow import get_log_uow_factory


__all__ = ['MonitoringMiddleware']


class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        error = False

        try:
            response = await call_next(request)
            return response
        except Exception:
            error = True
            raise
        finally:
            finish = time.monotonic()
            session_id = getattr(request.state, 'session_id', None)

            async with get_log_uow_factory()() as uow:
                await uow.monitoring_repository.add_monitoring(
                    path=request.url.path,
                    session_id=session_id,
                    status=not error,
                    duration=timedelta(seconds=finish - start)
                )
