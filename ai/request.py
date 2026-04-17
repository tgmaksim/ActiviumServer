from typing import Literal

from pydantic import BaseModel

from src.config.project_config import settings

from openai import AsyncOpenAI


client = AsyncOpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=settings.OPENROUTER_API_KEY
)


class Message(BaseModel):
    role: Literal['system', 'user', 'assistant']
    content: str


async def request(messages: list[Message]) -> str:
    response = await client.chat.completions.create(messages=[message.model_dump() for message in messages], model='openrouter/elephant-alpha')

    return response.choices[0].message.content
