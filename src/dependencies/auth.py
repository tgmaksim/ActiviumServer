from src.api.session_error import SessionError
from src.support.repositories.session_repository import SessionRepository

from src.models.session_model import Session


__all__ = ['check_session']


async def check_session(session_id: str, session_repository: SessionRepository, check_auth: bool = True) -> Session:
    """
    Получение сессии по ее идентификатору.
    Если сессии не существует или она не работает, то выбрасывается исключение SessionError

    :param session_id: идентификатор сессии
    :param session_repository: объект ``SessionRepository``
    :param check_auth: проверить ли авторизацию сессии
    :raise SessionError: сессия не существует или не авторизована
    :return: сессия, если она в порядке
    """

    session = await session_repository.get_session(session_id)
    if session is None or check_auth and session.parent_id is None:
        raise SessionError(session_id=session_id)

    return session
