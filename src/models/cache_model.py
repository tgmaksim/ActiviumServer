from typing import Union

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, BigInteger
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['Cache']


class Cache(BaseModel):
    """Модель кэша сервера"""

    session_id: Mapped[str] = mapped_column(
        String(32),
        comment="Идентификатор сессии"
    )
    child_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор ребенка"
    )
    key: Mapped[str] = mapped_column(
        String(64),
        comment="Уникальный ключ кэша"
    )
    value: Mapped[Union[list, dict]] = mapped_column(
        JSONB,
        comment="Значение кэша"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('session_id', 'child_id', 'key', name="caches_session_id_key_child_id"),

        ForeignKeyConstraint(
            ['session_id'],
            ['sessions.session_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="ea_processing_notifications_ea_id_fkey"
        ),
        ForeignKeyConstraint(
            ['child_id'],
            ['children.child_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="ea_processing_notifications_ea_child_id_fkey"
        )
    )
