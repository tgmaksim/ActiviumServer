from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .parent_model import Parent

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


__all__ = ['HighlightingPerson']


class HighlightingPerson(BaseModel):
    __tablename__ = 'highlighting_persons'

    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("parents.parent_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    person_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parent: Mapped['Parent'] = relationship('Parent', foreign_keys=[parent_id], lazy="selectin")
