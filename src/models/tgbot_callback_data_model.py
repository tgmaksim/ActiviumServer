from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, BigInteger
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Identity

from .base_model import BaseModel


__all__ = ['TgbotCallbackData']


class TgbotCallbackData(BaseModel):
    """Модель данных кнопок в Telegram-боте"""

    __tablename__ = 'tgbot_callback_data'

    module: Mapped[str] = mapped_column(
        String(15),
        comment="Идентификатор модуля Telegram-бота"
    )
    action: Mapped[str] = mapped_column(
        String(15),
        comment="Действие, совершаемое по кнопке"
    )
    key: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        comment="Ключ данных кнопки"
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        comment="Данные кнопки"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('module', 'action', 'key', name="tgbot_callback_data_module_key"),
    )
