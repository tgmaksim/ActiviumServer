from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


__all__ = ['SchoolAdmin']


class SchoolAdmin(BaseModel):
    """Модель администратора ОО"""

    __tablename__ = 'school_admins'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    parent_admin_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("school_admins.user_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    person_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    school_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    timezone: Mapped[int] = mapped_column(Integer, nullable=True)
    dnevnik_token: Mapped[str] = mapped_column(String(64), nullable=True)

    parent_admin: Mapped['SchoolAdmin'] = relationship(
        'SchoolAdmin', foreign_keys=[parent_admin_id], lazy="selectin")

    @property
    def dnevnik_admin(self) -> 'SchoolAdmin':
        """Получение своего или старшего администратора, который имеет данные Дневника.ру"""

        if self.parent_admin_id is None:
            return self

        return self.parent_admin.dnevnik_admin
