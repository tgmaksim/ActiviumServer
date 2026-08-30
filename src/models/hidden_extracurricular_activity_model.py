from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger, String
from sqlalchemy.sql.schema import PrimaryKeyConstraint

from .base_model import BaseModel


__all__ = ['HiddenExtracurricularActivity']


class HiddenExtracurricularActivity(BaseModel):
    """Модель скрытого внеурочного занятия"""

    __tablename__ = 'hidden_extracurricular_activities'

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор пользователя"
    )
    child_id: Mapped[int] = mapped_column(
        BigInteger,
        comment="Идентификатор профиля (ребенка)"
    )
    subject: Mapped[str] = mapped_column(
        String(32),
        comment="Название предмета внеурочного занятия"
    )
    place: Mapped[str] = mapped_column(
        String(32),
        comment="Место проведения (кабинет) внеурочного занятия"
    )

    __custom_table_args__ = (
        PrimaryKeyConstraint('parent_id', 'child_id', 'subject', 'place', name="hidden_extracurricular_activities_parent_id_child_id_subject_pl"),
    )
