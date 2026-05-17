from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .child_model import Child

from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import BigInteger, String, Boolean, TIMESTAMP
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['LessonNote']



class LessonNote(BaseModel):
    """Модель заметки к уроку"""

    __tablename__ = 'lesson_notes'

    child_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор ребенка"
    )
    lesson_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор урока в Дневнике.ру, к которому прикреплена заметка"
    )
    text: Mapped[str] = mapped_column(
        String(128),
        comment="Текст заметки"
    )
    public: Mapped[bool] = mapped_column(
        Boolean,
        comment="Открытые заметки видны родителям ребенка"
    )
    remind_time: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Время напоминания заметки"
    )

    child: Mapped['Child'] = relationship('Child', foreign_keys=[child_id], lazy="selectin")

    __custom_table_args__ = (
        PrimaryKeyConstraint('child_id', 'lesson_id', name="lesson_notes_child_id_lesson_id"),

        Index("lesson_notes_lesson_id_child_id", 'lesson_id', 'child_id'),

        ForeignKeyConstraint(
            ['child_id'],
            ['children.child_id'],
            onupdate='CASCADE',
            ondelete='CASCADE',
            name="lesson_notes_child_id_fkey"
        )
    )
