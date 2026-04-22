from dotenv import load_dotenv

from pydantic_settings import BaseSettings


__all__ = ['settings']


class TGBotSettings(BaseSettings):
    BOT_TOKEN: str
    URL: str
    BOT_URL: str  # Ссылка на Telegram-бота
    ADMIN_CHAT_IDS: list[int] = []
    AUTHOR_LINK: str

    GITHUB: str
    GITHUB_SERVER: str

    DNEVNIK_CLIENT_ID: str  # API-ключ для работы с Дневником.ру

    NETANGELS_GATEWAY_TOKEN_URL: str
    NETANGELS_API_KEY: str
    NETANGELS_API_URL: str
    VIRTUALHOST_ID: int


load_dotenv(dotenv_path=".env")
settings = TGBotSettings()
