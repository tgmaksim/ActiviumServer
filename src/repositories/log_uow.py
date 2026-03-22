from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .log_repository import LogRepository
from .sqlalchemy_uow import SqlAlchemyUnitOfWork
from .statistic_repository import StatisticRepository
from .monitoring_repository import MonitoringRepository
from .notification_repository import NotificationRepository


__all__ = ['LogUnitOfWork']


class LogUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory)

        self._log_repository: Optional[LogRepository] = None
        self._notification_repository: Optional[NotificationRepository] = None
        self._monitoring_repository: Optional[MonitoringRepository] = None
        self._statistics_repository: Optional[StatisticRepository] = None

    @property
    def log_repository(self) -> LogRepository:
        if self._log_repository is None:
            self._log_repository = LogRepository(self.session)
        return self._log_repository

    @property
    def notification_repository(self) -> NotificationRepository:
        if self._notification_repository is None:
            self._notification_repository = NotificationRepository(self.session)
        return self._notification_repository

    @property
    def monitoring_repository(self) -> MonitoringRepository:
        if self._monitoring_repository is None:
            self._monitoring_repository = MonitoringRepository(self.session)
        return self._monitoring_repository

    @property
    def statistics_repository(self) -> StatisticRepository:
        if self._statistics_repository is None:
            self._statistics_repository = StatisticRepository(self.session)
        return self._statistics_repository
