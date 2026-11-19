from pydantic import Field, BaseModel


__all__ = ['Subject', 'SubjectsList']


class Subject(BaseModel):
    """Доступный предмет в классе"""

    id: str = Field(
        description="Идентификатор учебного предмета"
    )
    name: str = Field(
        description="Название учебного предмета"
    )


SubjectsList = list[Subject]
