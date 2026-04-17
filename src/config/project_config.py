from typing import Optional

from dotenv import load_dotenv

from pydantic_settings import BaseSettings


__all__ = ['settings']


class Settings(BaseSettings):
    """Настройки проекта"""

    API_KEY: str  # Ключ для доступа к API
    CORS_ALLOWED_ORIGINS: list[str]

    DB_ECHO: bool = False  # Выводить в консоль все sql-запросы
    URL: str  # Домен (https://example.com), на котором запускается проект
    WWW_PATH: str  # Путь к папке со статическими ресурсами, которые отправляются низкоуровневым сервером
    NETANGELS_GATEWAY_TOKEN_URL: str
    NETANGELS_API_KEY: str
    NETANGELS_API_URL: str
    VIRTUALHOST_ID: int
    LOGS_PGADMIN_OPEN: str
    OPENROUTER_API_KEY: str
    API_PREFIX: str = "/api/v2"
    APK_PREFIX: str = "/apk"
    PROJECT_NAME: str = "Activium"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    AUTHOR: Optional[str] = None
    AUTHOR_LINK: Optional[str] = None
    ADMIN_TIMEZONE: int = 0
    HIDE_VALIDATION_ERRORS_IN_DOCS: bool = True  # Скрывать сущности Validation-ошибок в документации
    TEMPLATES_DIRECTORY: str = "templates"  # Папка в основной директории с html-фалами
    DNEVNIK_CLIENT_ID: str  # API-ключ для работы с Дневником.ру
    BOT_URL: str  # Ссылка на Telegram-бота


load_dotenv(dotenv_path=".env")
settings = Settings()  # Загрузка из env
