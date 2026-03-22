from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.child_model import Child
    from ..models.session_model import Session

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, TIMESTAMP, Text, func

from .base_model import BaseModel


__all__ = ['DnevnikNotification']


class DnevnikNotification(BaseModel):
    __tablename__ = 'dnevnik_notifications'

    session_id: Mapped[str] = mapped_column(Text(32), ForeignKey("sessions.session_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    child_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("children.child_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    last_mark: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    session: Mapped['Session'] = relationship('Session', foreign_keys=[session_id], lazy="selectin")
    child: Mapped['Child'] = relationship('Child', foreign_keys=[child_id], lazy="selectin")
