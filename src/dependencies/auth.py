from src.api.session_error import SessionError
from src.support.repositories.session_repository import SessionRepository

from src.models.session_model import Session


__all__ = ['check_session']


async def check_session(session_id: str, session_repository: SessionRepository) -> Session:
    """
    Получение сессии по идентификатору

    :param session_id: идентификатор сессии
    :param session_repository: объект ``SessionRepository``
    :raise SessionError
    :return: сессия
    """

    session = await session_repository.get_session(session_id)
    if session is None:
        raise SessionError(session_id=session_id)

    return session
