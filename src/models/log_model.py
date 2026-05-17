from typing import Optional

from sqlalchemy.sql import desc
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Text, Boolean, BigInteger
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, Identity

from .base_model import BaseModel


__all__ = ['Log']


class Log(BaseModel):
    """Модель лога"""

    log_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        comment="Идентификатор лога"
    )
    ip: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="IP-адрес, с которого совершен запрос, или модуль проекта, в котором записан лог"
    )
    path: Mapped[str] = mapped_column(
        Text,
        comment="Путь запроса или другая информация о месте записи лога"
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        comment="Идентификатор сессии, с которого сделан запрос"
    )
    status: Mapped[bool] = mapped_column(
        Boolean,
        comment="Успех операции"
    )
    method: Mapped[str] = mapped_column(
        String(32),
        nullable=True,
        comment="HTTP-метод запроса"
    )
    value: Mapped[str] = mapped_column(
        Text,
        comment="Данные лога"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('log_id', name="logs_log_id"),

        Index("logs_status_created_at", 'status', desc('created_at'))
    )
