from sqlalchemy import BigInteger, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['ExtracurricularActivity']


class ExtracurricularActivity(BaseModel):
    __tablename__ = 'extracurricular_activities'

    school_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    day_hash: Mapped[str] = mapped_column(Text(32), primary_key=True)
    subject: Mapped[str] = mapped_column(Text(32))
    place: Mapped[str] = mapped_column(Text(32))
    hours: Mapped[dict] = mapped_column(JSONB)
