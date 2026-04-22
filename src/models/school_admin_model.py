from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String

from .base_model import BaseModel


__all__ = ['SchoolAdmin']


class SchoolAdmin(BaseModel):
    __tablename__ = 'school_admins'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    parent_admin: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("school_admins.user_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    person_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    school_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    dnevnik_token: Mapped[str] = mapped_column(String(64), nullable=True)
