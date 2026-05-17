from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, Integer
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index

from .base_model import BaseModel


__all__ = ['Child']


class Child(BaseModel):
    """Модель ребенка (поставщик данных)"""

    __tablename__ = 'children'

    child_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор ребенка"
    )
    school_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор образовательной организации в Дневнике.ру"
    )
    group_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор учебной группы (класса) в Дневнике.ру"
    )
    timezone: Mapped[int] = mapped_column(
        Integer,
        comment="Часовой пояс ребенка в секундах"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('child_id', name="children_user_id"),

        Index("children_school_id_group_id_child_id", 'school_id', 'group_id', 'child_id')
    )
