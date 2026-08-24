import os
import signal

from httpx import AsyncClient

from src.config.project_config import settings

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory


__all__ = ['reload_server']


async def reload_server():
    """Перезагрузить сервер через API хостинга или через os.kill для debug-запуска"""

    if settings.DEBUG:
        # Отправка запроса на завершение процесса
        os.kill(os.getpid(), signal.SIGTERM)
        return

    async with AsyncClient() as client:
        response_token = await client.post(settings.HOSTING_GATEWAY_TOKEN_URL, data={'api_key': settings.HOSTING_API_KEY})
        token = response_token.json()['token']

        # С помощью полученного токена перезапускает полностью сервер
        response = await client.put(f"{settings.HOSTING_API_URL}/virtualhosts/{settings.VIRTUALHOST_ID}/restart/",
                                    headers={'Authorization': f'Bearer {token}'})

    service = LogService(get_log_uow_factory())
    await service.log(
        ip='127.0.0.1',
        path='reload',
        status=response.is_success,
        method=response.request.method,
        value=response.json() if not response.is_success else "Reload"
    )
