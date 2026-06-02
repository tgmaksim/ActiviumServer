from typing import Literal

from pydantic import BaseModel

from src.config.project_config import settings

from openai import AsyncOpenAI


__al__ = ['request', 'Message']

client = AsyncOpenAI(
  base_url=settings.OPENAI_URL,
  api_key=settings.OPENAI_API_KEY
)


class Message(BaseModel):
    """Сообщение в чате с ИИ"""

    role: Literal['system', 'user', 'assistant']
    """Роль пользователя, отправившего сообщение"""
    content: str
    """Текст сообщения"""


async def request(messages: list[Message]) -> str:
    """
    Запрос к ИИ с входными данными в виде чата

    :param messages: список сообщений с разными ролями
    :return: следующее сообщение от ИИ в виде строки
    """

    response = await client.chat.completions.create(
        messages=[message.model_dump() for message in messages],
        model=settings.OPENAI_MODEL
    )

    return response.choices[0].message.content
