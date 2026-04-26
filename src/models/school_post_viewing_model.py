from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['SchoolPostViewing']


class SchoolPostViewing(BaseModel):
    __tablename__ = 'school_post_viewings'

    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("parents.parent_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("school_posts.post_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
