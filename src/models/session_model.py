from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.child_model import Child
    from src.models.parent_model import Parent

from typing import Optional

from sqlalchemy import text as sql_text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String, BigInteger, Boolean
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint, CheckConstraint

from .base_model import BaseModel


__all__ = ['Session']


class Session(BaseModel):
    """Модель сессии"""

    session_id: Mapped[str] = mapped_column(
        String(32),
        comment="Идентификатор сессии"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор пользователя (пустой до авторизации)"
    )
    active_child_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор активного ребенка (пустой до авторизации)"
    )
    dnevnik_token: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="API-токен Дневника.ру для взаимодействия с ним (пустой до авторизации)"
    )
    firebase_token: Mapped[Optional[str]] = mapped_column(
        String(4096),
        nullable=True,
        comment="Firebase-токен для отправки уведомлений (пустой до авторизации)"
    )
    life: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sql_text('true'),
        comment="Сессия активна или больше не работает"
    )

    parent: Mapped['Parent'] = relationship('Parent', foreign_keys=[parent_id], lazy="selectin")
    active_child: Mapped['Child'] = relationship('Child', foreign_keys=[active_child_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('session_id', name="sessions_pkey"),

        Index("sessions_life_parent_id_session_id", 'life', 'parent_id', 'session_id'),
        Index("sessions_parent_id_life_session_id", 'parent_id', 'life', 'session_id'),
        Index("sessions_parent_id_session_id", 'parent_id', 'session_id'),

        CheckConstraint(
            "((((parent_id IS NULL) = (dnevnik_token IS NULL)) "
            "AND ((parent_id IS NULL) = (active_child_id IS NULL))))",
            name="check_full_auth"
        ),

        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="sessions_parent_id_fkey"
        ),
        ForeignKeyConstraint(
            ['active_child_id'],
            ['children.child_id'],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="sessions_active_child_id_fkey"
        )
    )
