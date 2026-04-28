from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['Parent']


class Parent(BaseModel):
    """Модель родителя (пользователя)"""

    parent_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
