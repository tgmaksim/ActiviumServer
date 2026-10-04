from yarl import URL

from dnevnikru import AioDnevnikruApi

from ...config.project_config import settings
from ..schemas.web_app_schemas import LoginUrl
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ...repositories.statistic_repository import StatName

from ...services.html_response import HtmlResponse


__all__ = ['WebAppService']


class WebAppService(BaseService[AppUnitOfWork]):
    """Сервис для работы web-приложения"""

    @classmethod
    def app(cls) -> HtmlResponse:
        return HtmlResponse(name='app.html')

    async def login(self) -> LoginUrl:
        async with self.uow_factory() as uow:
            await uow.statistic_repository.add_statistic(None, StatName.login)

        login_url = AioDnevnikruApi.build_login_url(
            dnevnikru_client_id=settings.DNEVNIK_CLIENT_ID,
            scope=["EducationalInfo", "CommonInfo", "FriendsAndRelatives"],
            redirect_uri=str(URL(settings.URL).joinpath("login", "web-auth")),
            state=""  # Сессия создается после авторизации
        )

        return LoginUrl(loginUrl=login_url)
