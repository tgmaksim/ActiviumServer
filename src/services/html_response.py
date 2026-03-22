from typing import Optional

from pydantic import BaseModel


__all__ = ['HtmlResponse']


class HtmlResponse(BaseModel):
    name: str
    status_code: int = 200
    context: Optional[dict] = {}
    cookies: Optional[dict] = None
