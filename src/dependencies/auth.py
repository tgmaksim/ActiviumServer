from typing import Annotated, Optional

from fastapi import Request, Header, Cookie, Depends
from fastapi.exceptions import RequestValidationError

from pydantic import ValidationError, BaseModel, model_validator

from ..api.session_error import SessionError
from .services import get_web_session_service
from ..support.services.web_session_service import WebSessionService


__all__ = ['get_session_id']


class AuthModel(BaseModel):
    sessionId: Optional[str] = None
    webSessionId: Optional[str] = None

    @model_validator(mode='after')
    def check(self):
        assert (self.sessionId is None) != (self.webSessionId is None), "sessionId xor webSessionId"
        return self


async def get_session_id(
        request: Request,
        sessionId: Annotated[Optional[str], Header(description="Идентификатор сессии", min_length=1, max_length=32)] = None,
        webSessionId: Annotated[Optional[str], Cookie(description="Идентификатор web-сессии", min_length=1, max_length=32)] = None,
        service: WebSessionService = Depends(get_web_session_service)
) -> str:
    try:
        AuthModel(sessionId=sessionId, webSessionId=webSessionId)
    except ValidationError as exc:
        raise RequestValidationError(errors=exc.errors()) from exc

    session_id = sessionId or await service.get_session_id(webSessionId)

    if session_id is None:
        raise SessionError(session_id=f"web-{webSessionId}")

    request.state.session_id = session_id

    return session_id
