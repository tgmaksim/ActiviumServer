from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.schemas.error_schema import ApiError

from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from src.api.base_api_exception import BaseApiException


__all__ = ['ApiException']


class ApiException(BaseApiException):
    """Исключение для выдачи ошибки в ответе API"""

    def __init__(self, /, error: 'ApiError', status_code: int = HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(error)

        self.error = error
        self.status_code = status_code
