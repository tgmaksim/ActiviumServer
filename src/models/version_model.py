from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Numeric, Integer, String, Text
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['Version']


class Version(BaseModel):
    """Модель версии приложения"""

    number: Mapped[int] = mapped_column(
        Integer,
        autoincrement=False,
        comment="Номер сборки версии"
    )
    version: Mapped[str] = mapped_column(
        String(16),
        comment="Строковая версия"
    )
    parent_version: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Главная версия группы"
    )
    status_id: Mapped[float] = mapped_column(
        Numeric,
        comment="Числовой статус, означающий важность обновления. (0;1]"
    )
    status: Mapped[str] = mapped_column(
        String(32),
        comment="Строковый статус, означающий важность обновления"
    )
    info: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        comment="Информационное сообщение, которое будет показана при запуске приложения с версией ниже"
    )
    logs: Mapped[str] = mapped_column(
        Text,
        comment="Список изменений, который будет показан пользователю"
    )
    date: Mapped[str] = mapped_column(
        String(16),
        comment="Дата выпуска обновления в строковом формате DD.MM.YYYY"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('number', name="versions_pkey"),

        ForeignKeyConstraint(
            ['parent_version'],
            ['versions.number'],
            ondelete='RESTRICT',
            onupdate='CASCADE',
            name="versions_parent_version_fkey"
        )
    )
