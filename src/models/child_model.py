from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['Child']


class Child(BaseModel):
    __tablename__ = 'children'

    child_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    school_id: Mapped[int] = mapped_column(BigInteger)
    group_id: Mapped[int] = mapped_column(BigInteger)
    timezone: Mapped[int] = mapped_column(Integer)
