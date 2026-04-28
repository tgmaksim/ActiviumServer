from typing import TypeVar, Generic, Callable

from ..repositories.base_uow import UnitOfWork


__all__ = ['BaseService']

UnitOfWorkType = TypeVar("UnitOfWorkType", bound=UnitOfWork)


class BaseService(Generic[UnitOfWorkType]):
    """Базовый сервис в UoW"""

    def __init__(self, uow_factory: Callable[[], UnitOfWorkType]):
        self.uow_factory = uow_factory
