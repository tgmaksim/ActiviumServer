from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.parent_model import Parent

from typing import Optional

from sqlalchemy import String, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


__all__ = ['Session']


class Session(BaseModel):
    session_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("parents.parent_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    dnevnik_token: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    firebase_token: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    life: Mapped[bool] = mapped_column(Boolean, default=True)
    parent: Mapped['Parent'] = relationship('Parent', foreign_keys=[parent_id], lazy="selectin")
