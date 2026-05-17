from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import Identity, Index, PrimaryKeyConstraint

from .base_model import BaseModel
from .hours_type import HoursType


__all__ = ['Hour']


class Hour(BaseModel):
    """Модель звонкового расписания, отличного от такого же в Дневнике.ру"""

    hour_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        comment="Идентификатор данных"
    )
    school_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор образовательной организации в Дневнике.ру"
    )
    months: Mapped[list[int]] = mapped_column(
        JSONB,
        comment="Список месяцев (номера), в которых действует расписание"
    )
    weekdays: Mapped[list[int]] = mapped_column(
        JSONB,
        comment="Список дней недели (индексы), в которых действует расписание"
    )
    hours: Mapped[list[HoursType]] = mapped_column(
        JSONB,
        comment="Список расписания звонков для каждого урока"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('hour_id', name="hours_hour_id"),

        Index("hours_school_id_months_weekdays", 'school_id', 'months', 'weekdays')
    )
