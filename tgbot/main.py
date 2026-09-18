import asyncio

from aiogram.utils.formatting import Text

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory

from src.utils.exception import format_exception

from .app import TgBotApp
from .enums.emoji import EmojiList


__all__ = ['add_polling_task']


async def run_polling():
    """Запуск Telegram-бота"""

    app =  TgBotApp()

    try:
        await app.send_to_admins(Text(EmojiList.rocket.value, "Бот запущен"))

        service = LogService(get_log_uow_factory())
        await service.log(ip='tgbot', path='tgbot', value="Бот запущен")

        print("Бот запущен")
        await app.run()
    except Exception as e:
        error = format_exception(e)

        service = LogService(get_log_uow_factory())
        await service.log(ip='tgbot', path='tgbot', value=error, status=False)

        print(error)
    finally:
        try:
            await app.send_to_admins(Text(EmojiList.brick.value, "Бот остановлен"))
        except Exception as e:
            print(format_exception(e))

        service = LogService(get_log_uow_factory())
        await service.log(path='tgbot', value="Бот остановлен")

        print("Бот остановлен")
        await app.shutdown()


def add_polling_task(loop: asyncio.AbstractEventLoop) -> asyncio.Task:
    """Запуск Telegram-бота в event loop"""

    return loop.create_task(run_polling())


if __name__ == "__main__":
    asyncio.run(run_polling())
