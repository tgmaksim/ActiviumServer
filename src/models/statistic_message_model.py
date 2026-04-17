from datetime import datetime

from sqlalchemy import String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


__all__ = ['StatisticMessage']


class StatisticMessage(BaseModel):
    __tablename__ = 'statistic_messages'

    time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True)
    message: Mapped[str] = mapped_column(String)
