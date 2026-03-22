from sqlalchemy import BigInteger, Identity
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['Hour']


class Hour(BaseModel):
    hour_id: Mapped[int] = mapped_column(BigInteger, Identity(always=False), primary_key=True)
    school_id: Mapped[int] = mapped_column(BigInteger)
    months: Mapped[list[int]] = mapped_column(JSONB)
    weekdays: Mapped[list[int]] = mapped_column(JSONB)
    hours: Mapped[list[dict[str, str]]] = mapped_column(JSONB)
