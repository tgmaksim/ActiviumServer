from typing import Union

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, BigInteger

from .base_model import BaseModel


__all__ = ['Cache']


class Cache(BaseModel):
    """Модель кэша сервера"""

    session_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("sessions.session_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    child_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("children.child_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[Union[list, dict]] = mapped_column(JSONB)
