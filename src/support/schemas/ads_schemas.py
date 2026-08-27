from typing import ClassVar, Literal, Optional

from pydantic import Field

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Ad', 'AdResult', 'AdApiResponse', 'ClickAdApiResponse']


class Ad(ApiBase):
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


class AdResult(ApiBase):
    """Результат запроса получения рекламного объявления"""

    classId: ClassVar[int] = 0x62
    class_id: Literal[0x62, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    ad: Optional[Ad] = Field(
        description="Рекламное объявление для показа, если доступно"
    )


class AdApiResponse(ApiResponse):
    """Ответ на запрос получения рекламного объявления"""

    classId: ClassVar[int] = 0x63
    class_id: Literal[0x63, 0x2] = Field(
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
