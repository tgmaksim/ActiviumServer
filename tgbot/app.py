from asyncio import gather
from contextlib import suppress

from aiogram import Bot, Dispatcher

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from .enums.commands import CommandList
from aiogram.utils.formatting import Text
from aiogram.types import BotCommand, BotCommandScopeChat, Message

from .services.fcm_storage import PostgresStorage
from .dependencies.uow import get_tgbot_uow_factory
from aiogram.fsm.storage.memory import SimpleEventIsolation

from src.config.project_config import settings

from .middlewares.auth import AuthMiddleware
from .middlewares.logging import LoggingMiddleware


__all__ = ['TgBotApp']


class TgBotApp:
    def __init__(self):
        self.bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        
        storage = PostgresStorage(get_tgbot_uow_factory())
        self.dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())

        self._register_middlewares()
        self._register_routers()
        
    def _register_middlewares(self):
        """Регистрация промежуточного ПО для Telegram-бота"""

        self.dp.update.outer_middleware(LoggingMiddleware())
        self.dp.message.middleware(AuthMiddleware())
        self.dp.callback_query.middleware(AuthMiddleware())

    def _register_routers(self):
        """Регистрация всех обработчиков событий для Telegram-бота"""

        from .modules.admin import handlers as admin_handlers
        from .modules.app import handlers as app_handlers
        from .modules.help import handlers as help_handlers
        from .modules.menu import handlers as menu_handlers
        from .modules.reviews import handlers as reviews_handlers
        from .modules.school import handlers as school_handlers
        from .modules.school_admins import handlers as school_admins_handlers
        from .modules.school_bells import handlers as school_bells_handlers
        from .modules.school_ea import handlers as school_ea_handlers
        from .modules.school_posts import handlers as school_posts_handlers
        from .modules.school_statistics import handlers as school_statistics_handlers
        from .modules.start import handlers as start_handlers

        self.dp.include_routers(
            admin_handlers.router,
            app_handlers.router,
            help_handlers.router,
            menu_handlers.router,
            school_handlers.router,
            reviews_handlers.router,

            school_admins_handlers.router,
            school_bells_handlers.router,
            school_ea_handlers.router,
            school_posts_handlers.router,
            school_statistics_handlers.router,

            start_handlers.router  # start всегда в конце, чтобы маршрутизировать deep link
        )

    async def run(self):
        """Запуск Telegram-бота"""

        await self._settings_my_commands()

        await self.dp.start_polling(self.bot)

    async def _settings_my_commands(self):
        """Добавление команд в меню Telegram-бота"""

        commands = [
            BotCommand(command='start', description="Запуск бота"),
            BotCommand(command=CommandList.start, description="Запуск бота"),
            BotCommand(command=CommandList.menu, description="Меню администратора ОО"),
            BotCommand(command=CommandList.school, description="Подключить ОО"),
            BotCommand(command=CommandList.help, description="О боте"),
            BotCommand(command=CommandList.app, description="Скачать приложение")
        ]

        my_commands = await self.bot.get_my_commands()
        if repr(my_commands) != repr(commands):
            await self.bot.set_my_commands(commands)

        admin_commands = [
            BotCommand(command=CommandList.reload, description=f"Перезапуск {settings.PROJECT_NAME_RU}"),
            BotCommand(command=CommandList.start, description="Запуск бота"),
            BotCommand(command=CommandList.menu, description="Меню администратора ОО"),
            BotCommand(command=CommandList.school, description="Подключить ОО"),
            BotCommand(command=CommandList.help, description="О боте"),
            BotCommand(command=CommandList.app, description="Скачать приложение")
        ]

        for admin in settings.ADMIN_CHAT_IDS:
            admin_scope = BotCommandScopeChat(chat_id=admin)
            my_admin_commands = await self.bot.get_my_commands(scope=admin_scope)
            if repr(my_admin_commands) != repr(admin_commands):
                await self.bot.set_my_commands(admin_commands, scope=admin_scope)

    async def send_to_admins(self, message: Text, **kwargs) -> list[Message]:
        """Отправка сообщений администраторам Telegram-бота"""

        return await gather(
            *(self.bot.send_message(
                admin,
                **message.as_kwargs(),
                **kwargs
            ) for admin in settings.ADMIN_CHAT_IDS)
        )

    async def shutdown(self):
        with suppress(RuntimeError):
            await self.dp.stop_polling()
        