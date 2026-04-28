from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['SchoolPostLike']


class SchoolPostLike(BaseModel):
    """Модель реакции на школьный пост"""

    __tablename__ = 'school_post_likes'

    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("parents.parent_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    post_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("school_posts.post_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
