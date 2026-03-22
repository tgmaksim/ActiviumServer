from typing import Callable

from ..repositories.log_uow import LogUnitOfWork
from ..support.repositories.app_uow import AppUnitOfWork

from ..config.database.db_helper import db_helper


__all__ = ['get_app_uow_factory', 'get_log_uow_factory']


def get_app_uow_factory() -> Callable[[], AppUnitOfWork]:
    def app_uow_factory() -> AppUnitOfWork:
        return AppUnitOfWork(db_helper.session_factory)

    return app_uow_factory


def get_log_uow_factory() -> Callable[[], LogUnitOfWork]:
    def log_uow_factory() -> LogUnitOfWork:
        return LogUnitOfWork(db_helper.session_factory)

    return log_uow_factory
