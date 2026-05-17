from datetime import datetime

from sqlalchemy import TIMESTAMP, func, Index, desc
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


__all__ = ['BaseModel']


class BaseModel(DeclarativeBase):
    """Базовая модель для всех моделей (таблиц) в БД"""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp()
    )

    __custom_table_args__ = ()

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    @declared_attr
    def __table_args__(cls) -> tuple:
        table_name = cls.__tablename__

        base_args = (
            Index(f"{table_name}_created_at", desc('created_at')),
        )

        return base_args + cls.__custom_table_args__
