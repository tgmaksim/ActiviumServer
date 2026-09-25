from typing import Annotated, Optional

from fastapi import Request, Header
from pydantic import ValidationError
from fastapi.params import Cookie, Depends
from fastapi.exceptions import RequestValidationError

from ..api.session_error import SessionError
from .services import get_web_session_service
from ..support.repositories.session_repository import SessionRepository
from ..support.services.web_session_service import WebSessionService

from ..models.session_model import Session


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


async def get_session_id(
        request: Request,
        sessionId: Annotated[Optional[str], Header(description="Идентификатор сессии", min_length=1, max_length=32)] = None,
        webSessionId: Annotated[Optional[str], Cookie(description="Идентификатор web-сессии", min_length=1, max_length=32)] = None,
        service: WebSessionService = Depends(get_web_session_service)
) -> str:
    if (sessionId is None) == (webSessionId is None):
        raise RequestValidationError(
            errors=ValidationError(
                "sessionId xor webSessionId "
                f"(sessionId: {sessionId}, webSessionId: {webSessionId})"
            ).errors()
        )

    if sessionId is None:
        sessionId = await service.get_session_id(webSessionId)

    request.state.session_id = sessionId

    return sessionId
