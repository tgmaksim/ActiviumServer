from typing import Optional

from sqlalchemy import Numeric, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['Version']


class Version(BaseModel):
    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(16))
    parent_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status_id: Mapped[float] = mapped_column(Numeric)
    status: Mapped[str] = mapped_column(String(32))
    info: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    logs: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String(16))
