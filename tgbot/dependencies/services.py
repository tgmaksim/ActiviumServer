import inspect

from typing import Type, Generic, TypeVar

from aiogram.filters import Filter
from aiogram.types import TelegramObject

from src.services.base_service import BaseService
from src.dependencies.httpx import get_httpx_client
from src.dependencies.uow import get_app_uow_factory

from ..dependencies.uow import get_tgbot_uow_factory


__all__ = ['ModuleService']

ModelType = TypeVar('ModelType', bound=BaseService)


class ModuleService(Filter, Generic[ModelType]):
    def __init__(self, service_type: Type[ModelType]):
        self.service_type = service_type

        signature = inspect.signature(self.service_type.__init__)
        self.valid_params = {name for name, param in signature.parameters.items()}

    async def __call__(self, event: TelegramObject) -> dict[str, ModelType]:
        params = {
            'uow_factory': get_app_uow_factory(),
            'tgbot_uow_factory': get_tgbot_uow_factory(),
            'httpx_client': get_httpx_client()
        }

        service = self.service_type(**{k: v for k, v in params.items() if k in self.valid_params})

        return {"service": service}
