from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.child_model import Child
    from ..models.session_model import Session

from sqlalchemy.sql.sqltypes import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['EANotification']


class EANotification(BaseModel):
    """Модель включенных уведомлений с напоминанием о внеурочной деятельности"""

    __tablename__ = 'ea_notifications'

    session_id: Mapped[str] = mapped_column(
        String(32),
        comment="Идентификатор сессии"
    )
    child_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор ребенка"
    )

    session: Mapped['Session'] = relationship('Session', foreign_keys=[session_id], lazy="selectin")
    child: Mapped['Child'] = relationship('Child', foreign_keys=[child_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('child_id', 'session_id', name="ea_notifications_child_id_session_id"),

        ForeignKeyConstraint(
            ['session_id'],
            ['sessions.session_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="ea_notifications_session_id_fkey"
        ),
        ForeignKeyConstraint(
            ['child_id'],
            ['children.child_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="ea_notifications_child_id_fkey"
        )
    )
