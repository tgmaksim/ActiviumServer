from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.child_model import Child
    from ..models.session_model import Session

from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.sqltypes import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    active_period_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,  # Только для работы миграции на новую версию
        comment="Идентификатор текущего отчетного периода"
    )
    marks: Mapped[list[dict]] = mapped_column(
        JSONB,
        comment="Все оценки за текущий отчетный период"
    )
    marks_hash: Mapped[str] = mapped_column(
        String(64),
        comment="Хэш списка оценок алгоритмом SHA-256"
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
