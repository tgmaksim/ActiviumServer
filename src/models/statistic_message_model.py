from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Text, TIMESTAMP
from sqlalchemy.sql.schema import PrimaryKeyConstraint

from .base_model import BaseModel


__all__ = ['StatisticMessage']


class StatisticMessage(BaseModel):
    """Модель сообщения администраторам с анализом логов, статистики и мониторинга"""

    __tablename__ = 'statistic_messages'

    time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        comment="Время сбора и анализа логов, мониторинга и статистики"
    )
    message: Mapped[str] = mapped_column(
        Text,
        comment="Итоговое сообщение с данными и анализом"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('time', name="statistic_messages_time"),
    )
