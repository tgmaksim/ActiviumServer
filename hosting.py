import os
import signal

from httpx import AsyncClient

from src.config.project_config import settings


__all__ = ['reload_server']


async def reload_server() -> dict:
    if settings.DEBUG:
        # Отправка запроса на завершение процесса
        os.kill(os.getpid(), signal.SIGTERM)

        return {
            'state': 'Active'
        }

    async with AsyncClient() as client:
        response_token = await client.post(settings.HOSTING_GATEWAY_TOKEN_URL, data={'api_key': settings.HOSTING_API_KEY})
        token = response_token.json()['token']

        # С помощью полученного токена перезапускает полностью сервер
        response = await client.put(f"{settings.HOSTING_API_URL}/virtualhosts/{settings.VIRTUALHOST_ID}/restart/",
                                    headers={'Authorization': f'Bearer {token}'})

        return response.json()
