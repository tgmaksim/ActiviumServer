from typing import Any
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Identity, TIMESTAMP, BOOLEAN, text, Integer

from .base_model import BaseModel


__all__ = ['SchoolPost']


class SchoolPost(BaseModel):
    __tablename__ = 'school_posts'

    post_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    school_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    date: Mapped[str] = mapped_column(String(10))
    schedule_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_updated: Mapped[bool] = mapped_column(BOOLEAN, server_default=text('false'))
    count_clicks: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    count_viewings: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    count_likes: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    content: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
