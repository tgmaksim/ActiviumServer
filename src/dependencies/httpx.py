from httpx import AsyncClient

from functools import lru_cache

from ..config.project_config import settings


__all__ = ['get_httpx_client']


@lru_cache()
def get_httpx_client() -> AsyncClient:
    """httpx-клиент для работы с сетевыми запросами. Кешируется на время работы"""

    return AsyncClient(headers={'User-Agent': f'{settings.PROJECT_NAME}/{settings.VERSION}'})
