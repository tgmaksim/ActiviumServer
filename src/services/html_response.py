from typing import Optional

from pydantic import BaseModel

from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from ..dependencies.templates import get_templates


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
    delete_cookies: list[dict] = []
    """Список cookies для удаления"""

    def to_response(self, request: Request) -> HTMLResponse:
        templates = get_templates()
        response = templates.TemplateResponse(
            request=request,
            name=self.name,
            status_code=self.status_code,
            context=self.context
        )

        if self.cookies:
            for cookie in self.cookies:
                response.set_cookie(**cookie)

        if self.delete_cookies:
            for cookie in self.delete_cookies:
                response.delete_cookie(**cookie)

        return response
