from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.ad_model import Ad
    from ..models.parent_model import Parent

from datetime import datetime

from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.sql.sqltypes import BigInteger, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['AdViewingModel']


class AdViewingModel(BaseModel):
    """Модель просмотра рекламы пользователем"""

    __tablename__ = 'ad_viewings'

    ad_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор рекламной единицы"
    )
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор пользователя"
    )
    last_viewing: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=current_timestamp(),
        comment="Время последнего показа рекламы пользователю"
    )

    ad: Mapped['Ad'] = relationship('Ad', foreign_keys=[ad_id], lazy="selectin")
    child: Mapped['Parent'] = relationship('Parent', foreign_keys=[parent_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('ad_id', 'parent_id', name="ad_viewings_ad_id_parent_id"),

        ForeignKeyConstraint(
            ['ad_id'],
            ['ads.ad_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="ad_viewings_ad_id_fkey"
        ),
        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="ad_viewings_parent_id_fkey"
        )
    )
