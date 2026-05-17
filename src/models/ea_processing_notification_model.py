from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.extracurricular_activity_model import ExtracurricularActivity

from datetime import datetime

from sqlalchemy.sql.sqltypes import BigInteger, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKeyConstraint, PrimaryKeyConstraint, Index

from .base_model import BaseModel


__all__ = ['EAProcessingNotification']


class EAProcessingNotification(BaseModel):
    """Модель внеурочных занятий, которые еще не обработаны для уведомлений"""

    __tablename__ = 'ea_processing_notifications'

    ea_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор внеурочного занятия"
    )
    start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        comment="Время начала внеурочного занятия"
    )

    extracurricular_activity: Mapped['ExtracurricularActivity'] = relationship(
        'ExtracurricularActivity', foreign_keys=[ea_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('ea_id', name="ea_processing_notifications_ea_id"),

        Index("ea_processing_notifications_start_time", 'start_time'),

        ForeignKeyConstraint(
            ['ea_id'],
            ['extracurricular_activities.ea_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="ea_processing_notifications_ea_id_fkey"
        )
    )
