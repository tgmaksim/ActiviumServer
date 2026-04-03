from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.extracurricular_activity_model import ExtracurricularActivity

from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


__all__ = ['EAProcessingNotification']


class EAProcessingNotification(BaseModel):
    __tablename__ = 'ea_processing_notifications'

    ea_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("extracurricular_activities.ea_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    extracurricular_activity: Mapped['ExtracurricularActivity'] = relationship('ExtracurricularActivity', foreign_keys=[ea_id], lazy="selectin")
