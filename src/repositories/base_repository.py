from abc import ABC, abstractmethod

from typing import Generic, TypeVar, Optional, Iterable

from ..models.base_model import BaseModel


__all__ = ['AbstractRepository', 'ModelType']

ModelType = TypeVar("ModelType", bound=BaseModel)


class AbstractRepository(ABC, Generic[ModelType]):
    """Абстрактный репозиторий с базовыми методами"""

    @abstractmethod
    async def create(self, data: dict, **kwargs) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    async def create_many(self, data: Iterable[dict], **kwargs) -> list[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, data: dict, *args, **kwargs) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def update_many(self, data: dict, *args, **kwargs) -> list[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_single(self, *args, **kwargs) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def get_first(self, *args, **kwargs) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def get_multi(self, *args, **kwargs) -> list[ModelType]:
        raise NotImplementedError
