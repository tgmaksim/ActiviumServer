from .base_api_exception import BaseApiException


__all__ = ['SessionError']


class SessionError(BaseApiException):
    """Сессия неверная"""

    def __init__(self, *, session_id: str):
        super().__init__(session_id)
        self.session_id = session_id
