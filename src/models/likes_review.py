from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['ReviewLike']


class ReviewLike(BaseModel):
    __tablename__ = 'review_likes'

    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("parents.parent_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    review_id: Mapped[str] = mapped_column(BigInteger, ForeignKey("reviews.parent_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
