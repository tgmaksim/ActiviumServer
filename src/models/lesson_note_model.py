from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, Text

from .base_model import BaseModel


__all__ = ['LessonNote']


class LessonNote(BaseModel):
    __tablename__ = 'lesson_notes'

    child_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("children.child_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(Text(128))
