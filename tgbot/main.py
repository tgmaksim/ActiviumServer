import asyncio
import traceback

from contextlib import suppress

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory

from src.config.project_config import settings
from .config.bot import create_bot_and_dispatcher


__all__ = ['add_polling_task']


async def run_polling():
    """Запуск прослушивания"""

    bot, dp = create_bot_and_dispatcher()

    try:
        await settings_my_commands(bot)

        for admin in settings.ADMIN_CHAT_IDS:
            await bot.send_message(admin, "<tg-emoji emoji-id=\"5445284980978621387\">🚀</tg-emoji> Бот запущен")

        service = LogService(get_log_uow_factory())
        await service.log(path='tgbot', value="Бот запущен")

        print("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        error = '\n'.join(traceback.format_exception(e))
        service = LogService(get_log_uow_factory())
        await service.log(path='tgbot', value=error, status=False)

        print(error)
    finally:
        for admin in settings.ADMIN_CHAT_IDS:
            await bot.send_message(admin, "<tg-emoji emoji-id=\"5260293700088511294\">⛔️</tg-emoji> Бот остановлен")

        service = LogService(get_log_uow_factory())
        await service.log(path='tgbot', value="Бот остановлен")

        print("Бот остановлен")
        with suppress(RuntimeError):
            await dp.stop_polling()


async def settings_my_commands(bot: Bot):
    """Добавление команд в меню"""

    commands = [
        BotCommand(command='start', description="Запуск бота"),
        BotCommand(command='menu', description="Меню администратора ОО"),
        BotCommand(command='school', description="Подключить ОО"),
        BotCommand(command='help', description="О боте"),
        BotCommand(command='app', description="Скачать приложение")
    ]

    my_commands = await bot.get_my_commands()
    if repr(my_commands) != repr(commands):
        await bot.set_my_commands(commands)

    admin_commands = [
        BotCommand(command='reload', description=f"Перезапуск {settings.PROJECT_NAME_RU}"),
        BotCommand(command='start', description="Запуск бота"),
        BotCommand(command='menu', description="Меню администратора ОО"),
        BotCommand(command='school', description="Подключить ОО"),
        BotCommand(command='help', description="О боте"),
        BotCommand(command='app', description="Скачать приложение")
    ]

    for admin in settings.ADMIN_CHAT_IDS:
        admin_scope = BotCommandScopeChat(chat_id=admin)
        my_admin_commands = await bot.get_my_commands(scope=admin_scope)
        if repr(my_admin_commands) != repr(admin_commands):
            await bot.set_my_commands(admin_commands, scope=admin_scope)


def add_polling_task(loop: asyncio.AbstractEventLoop) -> asyncio.Task:
    """Запуск прослушивания в event loop"""

    return loop.create_task(run_polling())


if __name__ == "__main__":
    asyncio.run(run_polling())
