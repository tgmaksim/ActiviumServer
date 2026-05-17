from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .parent_model import Parent

from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint

from .base_model import BaseModel


__all__ = ['HighlightingPerson']


class HighlightingPerson(BaseModel):
    """Модель выделенного одноклассника в рейтингах"""

    __tablename__ = 'highlighting_persons'

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор пользователя"
    )
    person_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор персоны в Дневнике.ру, который будет выделен в рейтинге"
    )

    parent: Mapped['Parent'] = relationship('Parent', foreign_keys=[parent_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('parent_id', 'person_id', name="highlighting_persons_parent_id_person_id"),

        CheckConstraint("((parent_id <> person_id))", name="check_no_self_person"),

        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="highlighting_persons_parent_id_fkey"
        )
    )
