from typing import Optional

from pydantic import BaseModel


__all__ = ['HtmlResponse']


class HtmlResponse(BaseModel):
    """Data-класс для возвращения ответа сервиса в виде html"""

    name: str
    """Имя файла в директории templates"""
    status_code: int = 200
    """http-код ответа"""
    context: Optional[dict] = {}
    """Параметры html-шаблона"""
    cookies: list[dict] = []
    """Список cookies"""
