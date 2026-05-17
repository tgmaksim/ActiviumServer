from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, String
from sqlalchemy.sql.schema import PrimaryKeyConstraint, Index, ForeignKeyConstraint, CheckConstraint

from .base_model import BaseModel


__all__ = ['Referral']


class Referral(BaseModel):
    """Модель связи пользователя с его приглашенными"""

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор пользователя, который пригласил пользователя"
    )
    referral_id: Mapped[int] = mapped_column(
        BigInteger,
        autoincrement=False,
        comment="Идентификатор пользователя, которого пригласили"
    )
    name: Mapped[str] = mapped_column(
        String(32),
        comment="Имя пригласившего (parent)"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('referral_id', name="referrals_referral_id"),

        Index("referrals_referral_id_parent_id", 'referral_id', 'parent_id'),
        Index("referrals_parent_id_referral_id", 'parent_id', 'referral_id'),

        CheckConstraint("((parent_id <> referral_id))", name="check_self_referral"),

        ForeignKeyConstraint(
            ['parent_id'],
            ['parents.parent_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="referrals_parent_id_fkey"
        ),
        ForeignKeyConstraint(
            ['referral_id'],
            ['parents.parent_id'],
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="referrals_referral_id_fkey"
        )
    )
