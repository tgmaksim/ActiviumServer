from .base_api_exception import BaseApiException


__all__ = ['ApiKeyError']


class ApiKeyError(BaseApiException):
    """API-ключ неверный"""

    def __init__(self, *, api_key: str, web_unauthorized: bool = False):
        super().__init__(api_key)
        self.api_key = api_key
        self.web_unauthorized = web_unauthorized
