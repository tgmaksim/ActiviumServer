from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint

from .base_model import BaseModel


__all__ = ['Teacher']


class Teacher(BaseModel):
    """Модель учителя"""

    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор учителя (Идентификатор персоны (person_id) в Дневнике.ру)"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('teacher_id', name="teachers_teacher_id"),
    )
