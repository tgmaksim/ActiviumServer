from datetime import timedelta

from sqlalchemy.sql import desc
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, Identity
from sqlalchemy.sql.sqltypes import String, Interval, BigInteger, Boolean

from .base_model import BaseModel


__all__ = ['Monitoring']


class Monitoring(BaseModel):
    """Модель мониторинга запросов"""

    monitoring_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        comment="Идентификатор записи мониторинга"
    )
    path: Mapped[str] = mapped_column(
        String(128),
        comment="Путь запроса"
    )
    session_id: Mapped[str] = mapped_column(
        String(32),
        nullable=True,
        comment="Идентификатор сессии"
    )
    status: Mapped[bool] = mapped_column(
        Boolean,
        comment="Статус запроса (отсутствие ошибки в процессе обработки)"
    )
    duration: Mapped[timedelta] = mapped_column(
        Interval,
        comment="Время обработки запроса"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('monitoring_id', name="monitorings_monitoring_id"),

        Index("monitorings_path_duration", 'path', desc('duration')),
        Index("monitorings_path_session_id_duration", 'path', 'session_id', desc('duration')),
        Index("monitorings_status_path_duration", desc('status'), 'path', desc('duration')),
        Index("monitorings_status_path_session_id_duration", desc('status'), 'path', 'session_id', desc('duration'))
    )
