from typing import ClassVar, Literal

from pydantic import BaseModel, Field


__all__ = ['ApiBase']


class ApiBase(BaseModel):
    classId: ClassVar[int] = 0x0  # Абстрактный класс
    class_id: Literal[0] = Field(
        alias='classId',  # Для проверки входящего classId
        description="Идентификатор класса"
    )
