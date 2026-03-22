import asyncio
import traceback

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory

from tgbot.config import settings
from .bot import create_bot_and_dispatcher


__all__ = ['add_polling_task']


async def run_polling():
    bot, dp = create_bot_and_dispatcher()

    try:
        for admin in settings.ADMIN_CHAT_IDS:
            await bot.send_message(admin, "🚀 Бот запущен")

        service = LogService(get_log_uow_factory())
        await service.log(path='tgbot', value="Бот запущен")

        print("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        service = LogService(get_log_uow_factory())
        await service.log(path='tgbot', value=f"{e.__class__.__name__}: {e}", status=False)

        print(''.join(traceback.format_exception(e)))
    finally:
        for admin in settings.ADMIN_CHAT_IDS:
            await bot.send_message(admin, "⛔ Бот остановлен")

        service = LogService(get_log_uow_factory())
        await service.log(path='tgbot', value="Бот остановлен")

        print("Бот остановлен")
        await bot.session.close()


def add_polling_task(loop: asyncio.AbstractEventLoop) -> asyncio.Task:
    return loop.create_task(run_polling())


if __name__ == "__main__":
    asyncio.run(run_polling())
