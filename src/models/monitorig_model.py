from datetime import timedelta

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Interval, BigInteger, Identity, Boolean

from .base_model import BaseModel


__all__ = ['Monitoring']


class Monitoring(BaseModel):
    monitoring_id: Mapped[int] = mapped_column(BigInteger, Identity(always=False), primary_key=True)
    path: Mapped[str] = mapped_column(String(128))
    session_id: Mapped[str] = mapped_column(String(32), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean)
    duration: Mapped[timedelta] = mapped_column(Interval)
