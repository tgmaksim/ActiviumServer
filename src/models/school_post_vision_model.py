from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['SchoolPostVision']


class SchoolPostVision(BaseModel):
    """Модель видения школьного поста (для подсчета неувиденных постов)"""

    __tablename__ = 'school_post_visions'

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор пользователя"
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор школьной публикации"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('parent_id', 'post_id', name="school_post_visions_parent_id_post_id"),

        Index("school_post_visions_post_id_parent_id", 'post_id', 'parent_id'),

        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="school_post_visions_parent_id_fkey"
        ),
        ForeignKeyConstraint(
            ['post_id'],
            ['school_posts.post_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="school_post_visions_post_id_fkey"
        )
    )
