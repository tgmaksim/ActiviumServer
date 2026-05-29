from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from ..project_config import load


__all__ = ['settings_db']


class ConfigDataBase(BaseSettings):
    """Конфигурация базы данных"""

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

    @property
    def database_url(self) -> str:
        """Формирование ссылки для соединения с БД"""

        return PostgresDsn.build(
            scheme=self.DB_SCHEME,
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USER,
            password=self.DB_PASS,
            path=self.DB_NAME,
        ).unicode_string()


load()

settings_db = ConfigDataBase()  # Загрузка из env
"""Настройки соединения с БД"""
