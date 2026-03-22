from dotenv import load_dotenv

from pydantic_settings import BaseSettings


__all__ = ['settings']


class TGBotSettings(BaseSettings):
    BOT_TOKEN: str
    URL: str
    ADMIN_CHAT_IDS: list[int] = []


load_dotenv(dotenv_path=".env")
settings = TGBotSettings()
