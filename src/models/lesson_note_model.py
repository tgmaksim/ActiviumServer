from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .child_model import Child

from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, Text, Boolean, TIMESTAMP

from .base_model import BaseModel


__all__ = ['LessonNote']



class LessonNote(BaseModel):
    __tablename__ = 'lesson_notes'

    child_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("children.child_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(Text(128))
    public: Mapped[bool] = mapped_column(Boolean)
    remind_time: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    child: Mapped['Child'] = relationship('Child', foreign_keys=[child_id], lazy="selectin")
