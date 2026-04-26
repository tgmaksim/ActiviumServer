import datetime

from typing import Any, Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Identity, TIMESTAMP, text, Integer, Boolean

from .base_model import BaseModel


__all__ = ['SchoolPost']


class SchoolPost(BaseModel):
    __tablename__ = 'school_posts'

    post_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    school_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    timezone: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    has_image: Mapped[bool] = mapped_column(Boolean)
    author: Mapped[str] = mapped_column(String(64))
    author_verified: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    schedule_date: Mapped[Optional[datetime.date]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_updated: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    count_visions: Mapped[int] = mapped_column(BigInteger, server_default=text('0'))
    count_clicks: Mapped[int] = mapped_column(BigInteger, server_default=text('0'))
    count_viewings: Mapped[int] = mapped_column(BigInteger, server_default=text('0'))
    count_likes: Mapped[int] = mapped_column(BigInteger, server_default=text('0'))
    content: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
