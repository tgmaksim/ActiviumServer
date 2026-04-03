from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.child_model import Child
    from ..models.session_model import Session

from sqlalchemy import BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


__all__ = ['EANotification']


class EANotification(BaseModel):
    __tablename__ = 'ea_notifications'

    session_id: Mapped[str] = mapped_column(Text(32), ForeignKey("sessions.session_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    child_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("children.child_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    session: Mapped['Session'] = relationship('Session', foreign_keys=[session_id], lazy="selectin")
    child: Mapped['Child'] = relationship('Child', foreign_keys=[child_id], lazy="selectin")
