from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .parent_model import Parent

from sqlalchemy.sql import desc
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import BigInteger, TIMESTAMP, String
from sqlalchemy.sql.schema import ForeignKeyConstraint, PrimaryKeyConstraint, Index

from datetime import datetime

from .base_model import BaseModel


__all__ = ['Information']


class Information(BaseModel):
    """Модель информационного сообщения для показа при запуске приложения"""

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор пользователя"
    )
    time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        comment="Целевое время информационного уведомления"
    )
    type: Mapped[str] = mapped_column(
        String(32),
        comment="Тип информации (для определенных действий после доставки)"
    )
    title: Mapped[str] = mapped_column(
        String(32),
        comment="Заголовок информационного уведомления"
    )
    text: Mapped[str] = mapped_column(
        String(128),
        comment="Текст информационного уведомления"
    )

    parent: Mapped['Parent'] = relationship('Parent', foreign_keys=[parent_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('parent_id', 'time', 'type', name="informations_parent_id_time_type"),

        Index("informations_time", desc('time')),

        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="informations_parent_id_fkey"
        )
    )
