from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String

from .base_model import BaseModel


__all__ = ['Referral']


class Referral(BaseModel):
    """Модель связи пользователя с его приглашенными"""

    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("parents.parent_id", onupdate="CASCADE", ondelete="CASCADE"))
    referral_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("parents.parent_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
