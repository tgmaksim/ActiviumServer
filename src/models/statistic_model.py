from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, BigInteger
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, Identity

from .base_model import BaseModel


__all__ = ['Statistic']


class Statistic(BaseModel):
    """Модель собранной статистики"""

    statistic_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        comment="Идентификатор статистики"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор пользователя, совершившего действие"
    )
    key: Mapped[str] = mapped_column(
        String(32),
        comment="Уникальный ключ действия"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('statistic_id', name="statistics_statistic_id"),

        Index("statistics_parent_id_key", 'parent_id', 'key')
    )
