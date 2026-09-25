from ...models.web_session_model import WebSession
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['WebSessionRepository']


class WebSessionRepository(SqlAlchemyRepository[WebSession]):
    """Репозиторий для взаимодействия с web-сессиями пользователей"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, WebSession)

    async def get_session(self, web_session_id: str) -> WebSession:
        """
        Получение полноценной сессии пользователя по идентификатору web-сессии

        :param web_session_id: идентификатор web-сессии
        :return: web-сессия пользователя
        """

        return await self.get_single(WebSession.web_session_id == web_session_id)
