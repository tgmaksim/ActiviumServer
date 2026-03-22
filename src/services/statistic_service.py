from .base_service import BaseService
from ..support.repositories.app_uow import AppUnitOfWork


__all__ = ['StatisticService']


class StatisticService(BaseService[AppUnitOfWork]):
    async def track(self, user_id: int, key: str) -> None:
        async with self.uow_factory() as uow:
            await uow.statistic_repository.add_statistic(user_id, key)
