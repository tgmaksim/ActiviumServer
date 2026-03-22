from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, Text, SmallInteger, Boolean, Integer

from .base_model import BaseModel


__all__ = ['Review']


class Review(BaseModel):
    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("parents.parent_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(Text(32))
    stars: Mapped[int] = mapped_column(SmallInteger)
    text: Mapped[str] = mapped_column(Text(256), nullable=True)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    is_updated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_open: Mapped[bool] = mapped_column(Boolean, default=False)
