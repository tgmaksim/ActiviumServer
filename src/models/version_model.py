from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import SmallInteger, Integer, String

from .base_model import BaseModel


__all__ = ['Version']


class Version(BaseModel):
    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(16))
    status_id: Mapped[int] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(String(32))
    logs: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String(16))
