from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .child_model import Child

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel


__all__ = ['Parent']


class Parent(BaseModel):
    parent_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    active_child_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("children.child_id", ondelete="RESTRICT", onupdate="CASCADE"))
    active_child: Mapped['Child'] = relationship('Child', foreign_keys=[active_child_id], lazy="selectin")
