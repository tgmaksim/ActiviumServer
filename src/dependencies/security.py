from typing import Annotated, Optional

from fastapi import Header, Cookie

from ..api.api_key_error import ApiKeyError
from ..config.project_config import settings


__all__ = ['check_api_key']


def check_api_key(
        apiKey: Annotated[str, Header(description="Ключ для доступа к API")],
        webSessionId: Annotated[Optional[str], Cookie(description="Идентификатор web-сессии", min_length=1, max_length=32)] = None
):
    """Зависимость fastapi для проверки API-ключа"""

    if webSessionId is not None:
        return  # Для web session пропускается любой API-ключ - он не является секретом

    if apiKey != settings.API_KEY:
        raise ApiKeyError(api_key=apiKey)
