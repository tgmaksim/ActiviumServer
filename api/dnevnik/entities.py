from typing import Optional, ClassVar, Literal

from pydantic import Field
from api.entities import ApiBase, ApiSession, ApiRequest, ApiResponse


__all__ = ['ScheduleApiRequest', 'ScheduleHomeworkDocument', 'ScheduleExtracurricularActivity', 'ScheduleHours',
           'ScheduleLesson', 'ScheduleDay', 'ScheduleResult', 'ScheduleApiResponse']


class ScheduleApiRequest(ApiRequest):
    classId: ClassVar[int] = 0x0000000D
    class_id: Literal[0x0000000D] = Field(
        alias='classId',
        description="Идентификатор класса"
    )

    data: ApiSession = Field(
        description="Данные сессии"
    )


class ScheduleHomeworkDocument(ApiBase):
    classId: ClassVar[int] = 0x0000000E
    class_id: Literal[0x0000000E] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    fileName: str = Field(
        description="Название файла",
        examples=["Задачи.docx"]
    )
    downloadUrl: str = Field(
        description="Ссылка для загрузки файла",
        examples=["https://b1.csdnevnik.ru/file.docx"]
    )


class ScheduleExtracurricularActivity(ApiBase):
    classId: ClassVar[int] = 0x0000000F
    class_id: Literal[0x0000000F] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    subject: str = Field(
        description="Название предмета внеурочки",
        examples=["Математика"]
    )
    place: str = Field(
        description="Кабинет или другое место проведения внеурочки",
        examples=["332"]
    )


class ScheduleHours(ApiBase):
    classId: ClassVar[int] = 0x00000010
    class_id: Literal[0x00000010] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    start: str = Field(
        description="Начало урока или внеурочки",
        examples=["08:00"]
    )
    end: str = Field(
        description="Окончание урока или внеурочки",
        examples=["08:40"]
    )


class ScheduleLesson(ApiBase):
    classId: ClassVar[int] = 0x00000011
    class_id: Literal[0x00000011] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    number: int = Field(
        description="Порядковый номер урока начиная с 0",
        examples=[0]
    )
    subject: str = Field(
        description="Название предмета урока",
        examples=["Математика"]
    )
    place: str = Field(
        description="Кабинет или другое место проведения урока",
        examples=["332"]
    )
    hours: ScheduleHours = Field(
        description="Время проведения урока"
    )
    homework: Optional[str] = Field(
        description="Домашнее задание к уроку",
        examples=["Доделать классную работу"]
    )
    files: list[ScheduleHomeworkDocument] = Field(
        description="Дополнительные файлы к домашнему заданию в виде списка из файлов"
    )


class ScheduleDay(ApiBase):
    classId: ClassVar[int] = 0x00000012
    class_id: Literal[0x00000012] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    date: str = Field(
        description="Дата дня в формате yyyy-MM-dd",
        examples=["2025-12-09"]
    )
    lessons: list[ScheduleLesson] = Field(
        description="Уроки в данный день в виде списка из уроков"
    )
    hoursExtracurricularActivities: Optional[ScheduleHours] = Field(
        description="Часы проведения внеурочек (если есть в данный день)"
    )
    extracurricularActivities: list[ScheduleExtracurricularActivity] = Field(
        description="Внеурочки в данный день (если есть) в виде списка внеурочек"
    )


class ScheduleResult(ApiBase):
    classId: ClassVar[int] = 0x00000013
    class_id: Literal[0x00000013] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    schedule: list[ScheduleDay] = Field(
        description="Расписание на 2 недели (15 дней) в виде списка из расписания на каждый день"
    )


class ScheduleApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x00000014
    class_id: Literal[0x00000014] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ScheduleResult] = Field(
        default=None,
        description="Данные о расписании на 2 недели (15 дней) ученика(цы)"
    )
