from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Numeric, Integer, String, Text
from sqlalchemy.sql.schema import PrimaryKeyConstraint, ForeignKeyConstraint

from .base_model import BaseModel


__all__ = ['WebVersion']


class WebVersion(BaseModel):
    """Модель версии web-приложения"""

    __tablename__ = 'web_versions'

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
    logs: Mapped[str] = mapped_column(
        Text,
        comment="Список изменений, который будет показан пользователю"
    )
    date: Mapped[str] = mapped_column(
        String(16),
        comment="Дата выпуска обновления в строковом формате DD.MM.YYYY"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('number', name="web_versions_pkey"),

        ForeignKeyConstraint(
            ['parent_version'],
            ['web_versions.number'],
            ondelete='RESTRICT',
            onupdate='CASCADE',
            name="web_versions_parent_version_fkey"
        )
    )
