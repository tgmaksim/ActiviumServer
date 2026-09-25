from sqlalchemy.sql.sqltypes import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint, UniqueConstraint

from .base_model import BaseModel


__all__ = ['WebSession']


class WebSession(BaseModel):
    """Модель web-сессии"""

    __tablename__ = 'web_sessions'

    web_session_id: Mapped[str] = mapped_column(
        String(32),
        comment="Идентификатор web-сессии"
    )
    session_id: Mapped[str] = mapped_column(
        String(32),
        comment="Идентификатор сессии"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('web_session_id', name="web_sessions_pkey"),

        UniqueConstraint('session_id', name="web_sessions_ukey"),

        Index("web_sessions_life", 'session_id'),

        ForeignKeyConstraint(
            ['session_id'],
            ['sessions.session_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="web_sessions_session_id_fkey"
        )
    )
