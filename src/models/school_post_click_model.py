from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['SchoolPostClick']


class SchoolPostClick(BaseModel):
    """Модель клика на школьный пост"""

    __tablename__ = 'school_post_clicks'

    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("parents.parent_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    post_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("school_posts.post_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
