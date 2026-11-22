from typing import ClassVar, Literal, Optional

from pydantic import Field

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Ad0x61', 'Ad', 'AdResult0x62', 'AdResult', 'AdApiResponse0x63', 'AdApiResponse', 'ClickAdApiResponse']


class Ad0x61(ApiBase):  # До версии API 2.3.0
    """Рекламное объявление"""

    classId: ClassVar[int] = 0x61
    class_id: Literal[0x61, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    adId: int = Field(
        description="Идентификатор рекламного объявления"
    )
    title: str = Field(
        description="Заголовок рекламного объявления"
    )
    text: str = Field(
        description="Текст рекламного объявления"
    )
    imageUrl: str = Field(
        description="Ссылка для скачивания рекламной картинки"
    )
    url: str = Field(
        description="URL для открытия страницы при нажатии на рекламу"
    )


class Ad(ApiBase):  # Начиная с версии API 2.4.0
    """Рекламное объявление"""

    classId: ClassVar[int] = 0x66
    class_id: Literal[0x66, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    adId: int = Field(
        description="Идентификатор рекламного объявления"
    )
    title: str = Field(
        description="Заголовок рекламного объявления"
    )
    text: str = Field(
        description="Текст рекламного объявления"
    )
    imageUrl: str = Field(
        description="Ссылка для скачивания рекламной картинки"
    )
    url: str = Field(
        description="URL для открытия страницы при нажатии на рекламу"
    )
    isDeveloperBirthday: bool = Field(
        description="Связана ли реклама с днем рождения разработчика для показа дополнительных анимаций"
    )


class AdResult0x62(ApiBase):  # До версии API 2.3.0
    """Результат запроса получения рекламного объявления"""

    classId: ClassVar[int] = 0x62
    class_id: Literal[0x62, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    ad: Optional[Ad0x61] = Field(
        description="Рекламное объявление для показа, если доступно"
    )


class AdResult(ApiBase):  # Начиная с версии API 2.4.0
    """Результат запроса получения рекламного объявления"""

    classId: ClassVar[int] = 0x67
    class_id: Literal[0x67, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    ad: Optional[Ad] = Field(
        description="Рекламное объявление для показа, если доступно"
    )


class AdApiResponse0x63(ApiResponse):  # До версии API 2.3.0
    """Ответ на запрос получения рекламного объявления"""

    classId: ClassVar[int] = 0x63
    class_id: Literal[0x63, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[AdResult0x62] = Field(
        default=None,
        description="Данные для показа рекламы"
    )


class AdApiResponse(ApiResponse):  # Начиная с версии API 2.4.0
    """Ответ на запрос получения рекламного объявления"""

    classId: ClassVar[int] = 0x68
    class_id: Literal[0x68, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[AdResult] = Field(
        default=None,
        description="Данные для показа рекламы"
    )


class ClickAdApiResponse(ApiResponse):
    """Ответ на запрос клика на рекламу"""

    classId: ClassVar[int] = 0x64
    class_id: Literal[0x64, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )
