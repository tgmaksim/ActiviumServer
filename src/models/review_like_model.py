from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['ReviewLike']


class ReviewLike(BaseModel):
    """Модель реакции на отзыв"""

    __tablename__ = 'review_likes'

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор пользователя"
    )
    review_id: Mapped[str] = mapped_column(
        BigInteger,
        comment="Идентификатор отзыва (идентификатор пользователя-владельца отзыва)"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('parent_id', 'review_id', name="likes_reviews_parent_id_review_id"),

        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="likes_reviews_parent_id_fkey"
        ),
        ForeignKeyConstraint(
            ['review_id'],
            ['reviews.parent_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="likes_reviews_review_id_fkey"
        )
    )
