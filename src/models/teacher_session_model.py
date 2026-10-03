from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.teacher_model import Teacher

from sqlalchemy import text as sql_text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String, BigInteger, Boolean
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['TeacherSession']


class TeacherSession(BaseModel):
    """Модель сессии учителя"""

    __tablename__ = 'teacher_sessions'

    session_id: Mapped[str] = mapped_column(
        String(32),
        comment="Идентификатор сессии учителя"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор учителя"
    )
    dnevnik_token: Mapped[str] = mapped_column(
        String(64),
        comment="API-токен Дневника.ру для взаимодействия с ним"
    )
    life: Mapped[bool] = mapped_column(
        Boolean,
        server_default=sql_text('true'),
        comment="Сессия активна или больше не работает"
    )

    teacher: Mapped['Teacher'] = relationship('Teacher', foreign_keys=[teacher_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('session_id', name="teacher_sessions_pkey"),

        Index("teacher_sessions_life_teacher_id_session_id", 'life', 'teacher_id', 'session_id'),
        Index("teacher_sessions_teacher_id_life_session_id", 'teacher_id', 'life', 'session_id'),
        Index("teacher_sessions_teacher_id_session_id", 'teacher_id', 'session_id'),

        ForeignKeyConstraint(
            ['teacher_id'],
            ['teachers.teacher_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="teacher_sessions_teacher_id_fkey"
        )
    )
