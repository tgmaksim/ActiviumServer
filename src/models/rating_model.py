from typing import Literal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, SmallInteger, ForeignKey, String

from .base_model import BaseModel


__all__ = ['Rating']


class Rating(BaseModel):
    child_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("children.child_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    period_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    number: Mapped[int] = mapped_column(SmallInteger)
    avg: Mapped[str] = mapped_column(String(8))
    mood: Mapped[Literal["good", "average", "bad", "more"]] = mapped_column(String(16))
