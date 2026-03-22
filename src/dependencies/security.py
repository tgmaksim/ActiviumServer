from typing import Annotated

from fastapi import Header

from ..api.api_key_error import ApiKeyError
from ..config.project_config import settings


__all__ = ['check_api_key']


def check_api_key(apiKey: Annotated[str, Header(description="Ключ для доступа к API")]):
    """Зависимость fastapi для проверки API-ключа"""

    if apiKey != settings.API_KEY:
        raise ApiKeyError(api_key=apiKey)
