from os import environ
from typing import Optional

from dotenv import load_dotenv

from pydantic_settings import BaseSettings


__all__ = ['settings']


class Settings(BaseSettings):
    """Настройки проекта"""

    # Базовые параметры
    PROJECT_NAME: str
    """Название проекта латиницей"""
    VERSION: str
    """Строковая версия сервера"""
    DEBUG: bool
    """Режим запуска сервера"""
    URL: str
    """Домен, на котором запускается проект"""
    WWW_PATH: str
    """Путь к папке со статическими ресурсами, которые отправляются низкоуровневым сервером"""

    # Параметры сервера
    COUNT_SERVER_WORKERS: int
    """Количество основных worker'ов сервера"""
    START_TGBOT_WORKER: bool
    """Запустить ли вместе с сервером worker Telegram-бота"""
    COUNT_MARKS_NOTIFICATIONS_WORKERS: int
    """Количество worker'ов уведомлений о новых оценках"""
    START_MARKS_NOTIFICATIONS_WORKER: bool
    """Запустить ли вместе с сервером worker уведомлений о новых оценках"""
    COUNT_EA_NOTIFICATIONS_WORKERS: int
    """Количество worker'ов уведомлений с напоминаниями о внеурочных занятиях"""
    START_EA_NOTIFICATIONS_WORKER: bool
    """Запустить ли worker уведомлений с напоминаниями о внеурочных занятий"""
    COUNT_NOTES_NOTIFICATIONS_WORKERS: int
    """Количество worker'ов уведомлений с напоминаниями о заметках к урокам"""
    START_NOTES_NOTIFICATIONS_WORKER: bool
    """Запустить ли worker уведомлений с напоминаниями о заметкам к урокам"""

    # Github
    GITHUB: str
    """Ссылка на github-репозиторий клиентского приложения"""
    GITHUB_SERVER: str
    """Ссылка на github-репозиторий сервера"""

    # Параметры хостинг-сервера
    HOSTING_GATEWAY_TOKEN_URL: str
    """URL для получения API-токена"""
    HOSTING_API_KEY: str
    """API-ключ для запроса получения токена"""
    HOSTING_API_URL: str
    """URL для API-запросов"""
    VIRTUALHOST_ID: int
    """Идентификатор сайта"""
    LOGS_PGADMIN_OPEN: str
    """Ссылка для открытия таблицы логов в БД с параметрами {min_created_at} и {max_created_at}"""

    # ИИ
    OPENAI_URL: str
    """URL OpenAI-сервера"""
    OPENAI_API_KEY: str
    """API-ключ для доступа к нейромодели через OpenAI"""
    OPENAI_MODEL: str
    """Идентификатор нейромодели"""

    # Telegram-бот
    BOT_TOKEN: str
    """Telegram-токен для работы бота"""
    ADMIN_CHAT_IDS: list[int]
    """Идентификаторы администраторов в Telegram"""
    BOT_URL: str
    """Ссылка на Telegram-бота"""
    TELEGRAM_PREVIEW_URL: str
    """URL proxy-сервера для предпросмотра изображений на сервере"""

    # API
    API_KEY: str
    """Ключ для доступа к API"""
    CORS_ALLOWED_ORIGINS: list[str]
    """Возможные домены, с которых доступно API в браузере"""
    API_PREFIX: str = "/api/v2"
    """Префикс пути всех API-методов"""
    APK_PREFIX: str = "/apk"
    """Префикс пути apk-файлов"""
    HIDE_VALIDATION_ERRORS_IN_DOCS: bool
    """Скрывать сущности Validation-ошибок в документации"""
    TEMPLATES_DIRECTORY: str
    """Папка в основной директории с html-файлами"""

    # Дневник.ру
    DNEVNIK_CLIENT_ID: str
    """API-ключ для работы с Дневником.ру"""

    # Автор
    AUTHOR: Optional[str] = None
    """Имя (псевдоним) автора проекта"""
    AUTHOR_LINK: Optional[str] = None
    """Ссылка на профиль в соц. сети автора проекта"""
    ADMIN_TIMEZONE: int = 0
    """Часовой пояс администраторов для оповещений"""

    # База данных
    DB_SCHEME: str
    """Scheme ссылки к БД"""
    DB_HOST: str
    """Host ссылки к БД"""
    DB_NAME: str
    """Имя БД"""
    DB_USER: str
    """Имя пользователя в БД"""
    DB_PASS: str
    """Пароль к пользователю в БД"""
    DB_PORT: int
    """Порт в ссылке к БД"""
    DB_ECHO: bool
    """Выводить в консоль все SQL-запросы"""


if environ.get('DEBUG'):
    load_dotenv(dotenv_path=".debug.env")
else:
    load_dotenv(dotenv_path=".env")
settings = Settings()  # Загрузка из env
"""Настройки проекта"""
