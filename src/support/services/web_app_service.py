from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork

from ...services.html_response import HtmlResponse


__all__ = ['WebAppService']


class WebAppService(BaseService[AppUnitOfWork]):
    """Сервис для работы web-приложения"""

    @classmethod
    def app(cls) -> HtmlResponse:
        return HtmlResponse(name='app.html')
