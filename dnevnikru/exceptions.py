class BaseDnevnikruException(Exception):
    """Базовый класс ошибок при взаимодействии с дневником.ру"""


class DnevnikruApiException(BaseDnevnikruException):
    """Ошибка в API-запросе от дневника.ру"""

    def __init__(self, _type: str, description: str):
        super().__init__(f"{_type}: {description}")
        self.type: str = _type
        self.description: str = description


class InvalidResponseException(BaseDnevnikruException):
    """Некорректный ответ от дневника.ру, привлекший к ошибке"""
