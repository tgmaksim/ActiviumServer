from typing import Literal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, SmallInteger, String
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['Rating']


class Rating(BaseModel):
    """Модель прошлого места в рейтинге с прошлым баллом"""

    child_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор ребенка"
    )
    period_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор отчетного периода в Дневнике.ру"
    )
    subject_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор учебного предмета в Дневнике.ру или -1 для общего рейтинга в классе"
    )
    number: Mapped[int] = mapped_column(
        SmallInteger,
        comment="Порядковый номер ребенка в рейтинге (индекс - начало с 0)"
    )
    avg: Mapped[str] = mapped_column(
        String(8),
        comment="Средний балл по предмету"
    )
    mood: Mapped[Literal["good", "average", "bad", "more"]] = mapped_column(
        String(16),
        comment="Настроение оценки в Дневнике.ру"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('child_id', 'period_id', 'subject_id', name="ratings_child_id_period_id_subject_id"),

        Index("ratings_period_id_child_id_subject_id", 'period_id', 'child_id', 'subject_id'),

        ForeignKeyConstraint(
            ['child_id'],
            ['children.child_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="ratings_child_id_fkey"
        )
    )
