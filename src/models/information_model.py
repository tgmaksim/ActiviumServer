from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .parent_model import Parent

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, TIMESTAMP, String

from datetime import datetime

from .base_model import BaseModel


__all__ = ['Information']


class Information(BaseModel):
    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("parents.parent_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True)
    type: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(128))
    parent: Mapped['Parent'] = relationship('Parent', foreign_keys=[parent_id], lazy="selectin")
