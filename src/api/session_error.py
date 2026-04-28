from .base_api_exception import BaseApiException


__all__ = ['SessionError']


class SessionError(BaseApiException):
    """Сессия не существует или не авторизована"""

    def __init__(self, *, session_id: str):
        super().__init__(session_id)
        self.session_id = session_id
