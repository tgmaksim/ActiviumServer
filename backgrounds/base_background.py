from typing import Callable
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

from httpx import AsyncClient

from firebase.messaging import FCMResult
from async_firebase.errors import UnregisteredError

from src.utils.exception import format_exception

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory
from src.support.repositories.app_uow import AppUnitOfWork


__all__ = ['BaseBackground']


class BaseBackground(ABC):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        self._running = False
        self.uow_factory = uow_factory
        self.httpx_client = httpx_client

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        raise NotImplementedError

    async def _start_run(self):
        self._running = True

        service = LogService(get_log_uow_factory())
        await service.log(
            ip=self.name(),
            path=self.name(),
            value="Worker запущен"
        )
        print(f"{self.name()} запущен")

    @asynccontextmanager
    async def run_context(self):
        await self._start_run()

        try:
            yield
        except Exception as e:
            service = LogService(get_log_uow_factory())
            await service.log(
                ip=self.name(),
                path=self.name(),
                status=False,
                value=format_exception(e)
            )
        finally:
            print(f"{self.name()} остановлен")
            service = LogService(get_log_uow_factory())
            await service.log(
                ip=self.name(),
                path=self.name(),
                value="Worker остановлен"
            )

    async def process_pushes(self, response: FCMResult):
        """Обработка результатов отправки уведомлений"""

        async with self.uow_factory() as uow:
            for firebase_token, result in (response.results if response else []):
                status = result.exception is None
                await uow.log_repository.add_log(
                    ip=self.name(),
                    path=firebase_token,
                    status=status,
                    value=f"{result.exception}: {result.exception.http_response} "
                          f"{result.exception.cause} " if not status else str(result)
                )

                # Если firebase_token не зарегистрирован в системе FCM, то сессия становится не работающей,
                # потому что приложение удалено либо было очищено
                if isinstance(result.exception, UnregisteredError):
                    await uow.session_repository.kill_sessions_by_firebase_token(firebase_token)

    def stop(self):
        self._running = False
