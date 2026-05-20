import datetime

from typing import Optional
from typing import TypedDict, Literal

from sqlalchemy import desc, text as sql_text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, String, Date, Integer, Boolean
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, Identity, CheckConstraint

from .base_model import BaseModel


__all__ = ['SchoolPost', 'SchoolPostContentType', 'SchoolPostContentEntityType']


class SchoolPostContentEntityType(TypedDict):
    """Форматирование в публикации"""

    offset: int
    length: int
    type: str
    url: Optional[str]


class SchoolPostContentType(TypedDict):
    """Формат контента школьного поста"""

    type: Literal['title', 'text', 'photo', 'video']
    text: str
    entities: list[SchoolPostContentEntityType]


class SchoolPost(BaseModel):
    """Модель опубликованного школьного поста"""

    __tablename__ = 'school_posts'

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        comment="Идентификатор школьной публикации"
    )
    school_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор образовательной организации в Дневнике.ру. Если не указано, то открыто для для всех"
    )
    timezone: Mapped[int] = mapped_column(
        Integer,
        comment="Часовой пояс в секундах"
    )
    title: Mapped[str] = mapped_column(
        String(128),
        comment="Заголовок публикации"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        comment="Описание публикации под заголовком"
    )
    has_image: Mapped[bool] = mapped_column(
        Boolean,
        comment="Наличие главного изображения публикации"
    )
    author: Mapped[str] = mapped_column(
        String(64),
        comment="Автор публикации (администратор образовательной организации или другое)"
    )
    author_verified: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sql_text('false'),
        comment="Автор является официальным лицом приложения"
    )
    schedule_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        nullable=True,
        comment="Дата проведенного мероприятия"
    )
    is_updated: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sql_text('false'),
        comment="Публикация была отредактирована"
    )
    count_visions: Mapped[int] = mapped_column(
        BigInteger,
        server_default=sql_text('0'),
        comment="Количество пользователей, которые увидели наличие публикации"
    )
    count_clicks: Mapped[int] = mapped_column(
        BigInteger,
        server_default=sql_text('0'),
        comment="Количество пользователей, которые открыли публикации"
    )
    count_viewings: Mapped[int] = mapped_column(
        BigInteger,
        server_default=sql_text('0'),
        comment="Количество полных просмотров публикации"
    )
    count_likes: Mapped[int] = mapped_column(
        BigInteger,
        server_default=sql_text('0'),
        comment="Количество реакции на публикацию"
    )
    content: Mapped[list[SchoolPostContentType]] = mapped_column(
        JSONB,
        comment="Содержание публикации - последовательные заголовки, абзацы, фото и видео"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('post_id', name="school_posts_post_id"),

        CheckConstraint("((count_visions >= 0))", name="check_count_visions"),
        CheckConstraint("((count_clicks >= 0))", name="check_count_clicks"),
        CheckConstraint("((count_viewings >= 0))", name="check_count_views"),
        CheckConstraint("((count_likes >= 0))", name="check_count_likes"),

        Index("school_posts_school_id_created_at", 'school_id', desc('created_at'))
    )
