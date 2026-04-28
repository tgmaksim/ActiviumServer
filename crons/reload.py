from hosting import reload_server


__all__ = ['main']


async def main():
    """Перезапуск сервера"""

    await reload_server()
