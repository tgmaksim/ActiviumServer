from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['WebSessionService']


class WebSessionService(BaseService[AppUnitOfWork]):
    """Сервис для взаимодействия с web-сессией"""

    async def get_session_id(self, web_session_id: str) -> str:
        async with self.uow_factory() as uow:
            session = await uow.web_session_repository.get_session(web_session_id)

            return session.session_id
