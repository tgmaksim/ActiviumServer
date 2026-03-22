from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Identity

from .base_model import BaseModel


__all__ = ['Statistic']


class Statistic(BaseModel):
    statistic_id: Mapped[int] = mapped_column(BigInteger, Identity(always=False), primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    key: Mapped[str] = mapped_column(String(32))
