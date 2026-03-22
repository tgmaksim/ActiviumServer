from abc import ABC, abstractmethod

from typing import Generic, TypeVar, Optional

from ..models.base_model import BaseModel


__all__ = ['AbstractRepository', 'ModelType']

ModelType = TypeVar("ModelType", bound=BaseModel)


class AbstractRepository(ABC, Generic[ModelType]):
    @abstractmethod
    async def create(self, data: dict) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    async def update(self, data: dict, **kwargs) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_single(self, *args, **kwargs) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def get_multi(self, *args, **kwargs) -> list[ModelType]:
        raise NotImplementedError
