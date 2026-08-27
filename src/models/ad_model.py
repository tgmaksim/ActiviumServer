from typing import Optional

from sqlalchemy.sql import text as sql_text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, Identity
from sqlalchemy.sql.sqltypes import BigInteger, String, Boolean, Integer

from .base_model import BaseModel


__all__ = ['Ad']


class Ad(BaseModel):
    """Модель рекламной единицы"""

    ad_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        comment="Идентификатор рекламной единицы"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор пользователя в Telegram, который управляет рекламой"
    )
    school_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор образовательной организации, в которой доступна реклама"
    )
    group_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор учебной группы (класса), в которой доступна реклама"
    )
    title: Mapped[str] = mapped_column(
        String(32),
        comment="Заголовок рекламы"
    )
    text: Mapped[str] = mapped_column(
        String(128),
        comment="Текст рекламы"
    )
    has_image: Mapped[bool] = mapped_column(
        Boolean,
        comment="Наличие у рекламы собственной картинки"
    )
    url: Mapped[str] = mapped_column(
        String(1024),
        comment="URL, на который будет перенаправлен пользователь при открытии рекламы"
    )
    balance: Mapped[int] = mapped_column(
        Integer,
        comment="Количество доступных показов"
    )
    clicks: Mapped[int] = mapped_column(
        Integer,
        server_default=sql_text('0'),
        comment="Количество кликов на рекламу"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('ad_id', name="ads_ad_id"),

        Index("ads_school_id_group_id_balance", 'school_id', 'group_id', 'balance'),
        Index("ads_user_id", 'user_id')
    )
