from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, BigInteger, Boolean

from .base_model import BaseModel


__all__ = ['Notification']


class Notification(BaseModel):
    log_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("logs.log_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    ip: Mapped[Optional[str]] = mapped_column(String(39), nullable=True)
    path: Mapped[str] = mapped_column(String(128))
    session_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean)
    method: Mapped[str] = mapped_column(String(8), nullable=True)
    value: Mapped[str] = mapped_column(String)
