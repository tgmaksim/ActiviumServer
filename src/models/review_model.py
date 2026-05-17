from sqlalchemy.sql import desc, text as sql_text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, String, SmallInteger, Boolean, Integer
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint, CheckConstraint

from .base_model import BaseModel


__all__ = ['Review']


class Review(BaseModel):
    """Модель отзыва"""

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор пользователя"
    )
    name: Mapped[str] = mapped_column(
        String(32),
        comment="Имя пользователя, написавшего отзыв"
    )
    stars: Mapped[int] = mapped_column(
        SmallInteger,
        comment="Количество звезд в отзыве"
    )
    text: Mapped[str] = mapped_column(
        String(512),
        nullable=True,
        comment="Текст отзыва"
    )
    likes: Mapped[int] = mapped_column(
        Integer,
        server_default=sql_text('0'),
        comment="Количество реакции на отзыве"
    )
    is_updated: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sql_text('false'),
        comment="Отзыв был отредактирован"
    )
    is_open: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sql_text('false'),
        comment="Отзыв открыт и доступен для показа или находится на модерации"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('parent_id', name="reviews_parent_id"),

        Index("reviews_is_open_stars_likes_created_at",
              desc('is_open'), desc('stars'), desc('likes'), desc('created_at')),
        Index("reviews_is_open_min_stars_likes_created_at",
              desc('is_open'), 'stars', desc('likes'), desc('created_at')),
        Index("reviews_is_open_likes_created_at", desc('is_open'), desc('likes'), desc('created_at')),

        CheckConstraint("(((stars >= 1) AND (stars <= 5)))", name="check_stars"),
        CheckConstraint("((likes >= 0))", name="check_likes"),

        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="reviews_parent_id_fkey"
        )
    )
