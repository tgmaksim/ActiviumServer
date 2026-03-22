from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, BigInteger, Identity

from .base_model import BaseModel


__all__ = ['Log']


class Log(BaseModel):
    log_id: Mapped[int] = mapped_column(BigInteger, Identity(always=False), primary_key=True)
    ip: Mapped[Optional[str]] = mapped_column(String(39), nullable=True)
    path: Mapped[str] = mapped_column(String(128))
    session_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean)
    method: Mapped[str] = mapped_column(String(8), nullable=True)
    value: Mapped[str] = mapped_column(String)
