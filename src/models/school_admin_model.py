from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import BigInteger, String, Integer, Boolean
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint, CheckConstraint

from .base_model import BaseModel


__all__ = ['SchoolAdmin']


class SchoolAdmin(BaseModel):
    """Модель администратора ОО"""

    __tablename__ = 'school_admins'

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор Telegram-аккаунта администратора образовательной организации"
    )
    name: Mapped[str] = mapped_column(
        String(64),
        comment="Имя администратора образовательной организации"
    )
    parent_admin_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор верхнего по уровню администратора образовательной организации (user_id)"
    )
    life: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Сессия администратора образовательной организации активна или больше не работает"
    )
    person_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор персоны в Дневнике.ру (для самого верхнего по уровню администратора образовательной организации)"
    )
    school_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Идентификатор образовательной организации в Дневнике.ру (для самого верхнего по уровню администратора образовательной организации)"
    )
    timezone: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Часовой пояс в секундах (для самого верхнего по уровню администратора образовательной организации)"
    )
    dnevnik_token: Mapped[str] = mapped_column(
        String(64),
        nullable=True,
        comment="API-токен Дневника.ру (для самого верхнего по уровню администратора образовательной организации)"
    )

    parent_admin: Mapped['SchoolAdmin'] = relationship(
        'SchoolAdmin', foreign_keys=[parent_admin_id], remote_side=[user_id], lazy="raise")

    __custom_table_args__ = (
        PrimaryKeyConstraint('user_id', name="school_admins_user_id"),

        Index("school_admins_school_id_person_id", 'school_id', 'person_id'),
        Index("school_admins_school_id_user_id", 'school_id', 'user_id'),
        Index("school_admins_parent_admin_user_id", 'parent_admin_id', 'user_id'),

        CheckConstraint("((user_id <> parent_admin_id))", name="check_no_self_admin"),
        CheckConstraint(
            "((((parent_admin_id IS NULL) <> (person_id IS NULL)) "
            "AND ((parent_admin_id IS NULL) <> (school_id IS NULL)) "
            "AND ((parent_admin_id IS NULL) <> (dnevnik_token IS NULL)) "
            "AND ((parent_admin_id IS NULL) <> (timezone IS NULL))))"
            "AND ((parent_admin_id IS NULL) <> (life IS NULL))",
            name="check_type_admin"
        ),

        ForeignKeyConstraint(
            ['parent_admin_id'],
            ['school_admins.user_id'],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="school_admins_parent_admin_fkey"
        )
    )

    @property
    def dnevnik_admin(self) -> 'SchoolAdmin':
        """Получение своего или старшего администратора, который имеет данные Дневника.ру"""

        if self.parent_admin_id is None:
            return self

        return self.parent_admin.dnevnik_admin
