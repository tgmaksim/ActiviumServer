from typing import Any

from sqlalchemy import text as sql_text
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint

from .base_model import BaseModel


__all__ = ['TgbotState']


class TgbotState(BaseModel):
    """Модель состояния пользователя в Telegram-боте"""

    __tablename__ = 'tgbot_states'

    key: Mapped[str] = mapped_column(
        String(128),
        comment="Ключ из чата и пользователя"
    )
    state: Mapped[str] = mapped_column(
        String(128),
        nullable=True,
        comment="Состояние (действие, которое ожидается от пользователя)"
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default=sql_text("'{}'"),
        comment="Дополнительные данные к состоянию"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('key', name="tgbot_states_key"),
    )
