from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, TIMESTAMP, Identity, UniqueConstraint

from .base_model import BaseModel


__all__ = ['ExtracurricularActivity']


class ExtracurricularActivity(BaseModel):
    __tablename__ = 'extracurricular_activities'

    ea_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    school_id: Mapped[int] = mapped_column(BigInteger)
    group_id: Mapped[int] = mapped_column(BigInteger)
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    subject: Mapped[str] = mapped_column(Text(32))
    place: Mapped[str] = mapped_column(Text(32))
    hours: Mapped[dict] = mapped_column(JSONB)

    __table_args__ = (
        UniqueConstraint('school_id', 'group_id', 'start_time', 'subject', 'place', name='extracurricular_activities_school_id_group_id_start_time_subjec'),
    )
