from ...config.project_config import settings

from ...services.html_response import HtmlResponse

from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['TgWebAppService']


class TgWebAppService(BaseService[AppUnitOfWork]):
    """Сервис для работы сайта"""

    @classmethod
    async def bells(cls) -> HtmlResponse:
        return HtmlResponse(name='bells_editor.html', context={'project_name': settings.PROJECT_NAME_RU})

    @classmethod
    async def extracurricular_activity_edit(cls) -> HtmlResponse:
        return HtmlResponse(name='ea_edit.html', context={'project_name': settings.PROJECT_NAME_RU})
