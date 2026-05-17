from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, String, TIMESTAMP
from sqlalchemy.sql.schema import Identity, PrimaryKeyConstraint, UniqueConstraint, Index

from .base_model import BaseModel
from .hours_type import HoursType


__all__ = ['ExtracurricularActivity']


class ExtracurricularActivity(BaseModel):
    """Модель внеурочного занятия в расписании"""

    __tablename__ = 'extracurricular_activities'

    ea_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        comment="Идентификатор внеурочного занятия"
    )
    school_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор образовательной организации в Дневнике.ру"
    )
    group_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор учебной группы (класса) в Дневнике.ру"
    )
    start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        comment="Время начала внеурочного занятия"
    )
    subject: Mapped[str] = mapped_column(
        String(32),
        comment="Название предмета внеурочного занятия"
    )
    place: Mapped[str] = mapped_column(
        String(32),
        comment="Место проведения (кабинет) внеурочного занятия"
    )
    hours: Mapped[HoursType] = mapped_column(
        JSONB,
        comment="Часы проведения внеурочного занятия"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('ea_id', name="extracurricular_activities_pkey"),

        UniqueConstraint('school_id', 'group_id', 'start_time', 'subject', 'place',
                         name='extracurricular_activities_school_id_group_id_start_time_subjec'),

        Index("extracurricular_activities_start_time_subject_place", 'start_time', 'subject', 'place')
    )
