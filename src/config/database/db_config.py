from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


__all__ = ['settings_db']


class ConfigDataBase(BaseSettings):
    """Конфигурация базы данных"""

    DB_SCHEME: str
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: int = 5432

    DB_ECHO: bool = False  # Выводить в консоль все sql-запросы

    @property
    def database_url(self) -> str:
        return PostgresDsn.build(
            scheme=self.DB_SCHEME,
            host=self.DB_HOST,
            port=self.DB_PORT,
            username=self.DB_USER,
            password=self.DB_PASS,
            path=self.DB_NAME,
        ).unicode_string()


settings_db = ConfigDataBase()  # Загрузка из env
