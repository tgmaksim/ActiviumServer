from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.child_model import Child
    from ..models.session_model import Session

from datetime import datetime

from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import BigInteger, TIMESTAMP, String
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['MarksNotification']


class MarksNotification(BaseModel):
    """Модель включенных уведомлений о новых оценках"""

    __tablename__ = 'marks_notifications'

    session_id: Mapped[str] = mapped_column(
        String(32),
        comment="Идентификатор сессии"
    )
    child_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор ребенка"
    )
    last_mark: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=current_timestamp(),
        comment="Точное время постановки последней оценки от Дневника.ру"
    )

    session: Mapped['Session'] = relationship('Session', foreign_keys=[session_id], lazy="selectin")
    child: Mapped['Child'] = relationship('Child', foreign_keys=[child_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('child_id', 'session_id', name="marks_notifications_child_id_session_id"),

        ForeignKeyConstraint(
            ['session_id'],
            ['sessions.session_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="marks_notifications_session_id_fkey"
        ),
        ForeignKeyConstraint(
            ['child_id'],
            ['children.child_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="marks_notifications_child_id_fkey"
        )
    )
