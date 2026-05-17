from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint

from .base_model import BaseModel


__all__ = ['Parent']


class Parent(BaseModel):
    """Модель родителя (пользователя)"""

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор пользователя (Идентификатор персоны (person_id) в Дневнике.ру)"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('parent_id', name="parents_user_id"),
    )
