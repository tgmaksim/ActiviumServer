from pydantic import Field
from typing import Optional, ClassVar, Literal

from api.entities import ApiBase, ApiSession, ApiRequest, ApiResponse


__all__ = ['ScheduleApiRequest0x0000000D', 'ScheduleApiRequest0x00000015', 'ScheduleApiRequest0x00000022',
           'ScheduleInputData', 'ScheduleApiRequest', 'ScheduleHomeworkDocument', 'ScheduleExtracurricularActivity',
           'ScheduleHours', 'MarksOther', 'MarkLog', 'ScheduleLesson0x00000011', 'ScheduleLesson',
           'ScheduleDay0x00000012', 'ScheduleDay', 'ScheduleResult0x00000013', 'ScheduleResult0x00000019',
           'ScheduleResult', 'ScheduleApiResponse0x00000014', 'ScheduleApiResponse0x00000020', 'ScheduleApiResponse']


class ScheduleApiRequest0x0000000D(ApiRequest):
    """Запрос расписания на 2 недели (15 дней) устаревшая версия"""

    classId: ClassVar[int] = 0x0000000D
    class_id: Literal[0x0000000D] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: ApiSession = Field(
        description="Данные сессии"
    )


class ScheduleApiRequest0x00000015(ApiRequest):
    """Запрос расписания на 2 недели (15 дней) устаревшая версия"""

    classId: ClassVar[int] = 0x00000015
    class_id: Literal[0x00000015] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: ApiSession = Field(
        description="Данные сессии"
    )


class ScheduleApiRequest0x00000022(ApiRequest):
    """Запрос расписания на 3 недели (22 дня): 7 дней до сегодня, сегодня и 15 дней после устаревшая версия"""

    classId: ClassVar[int] = 0x00000022
    class_id: Literal[0x00000022] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: ApiSession = Field(
        description="Данные сессии"
    )


class ScheduleInputData(ApiBase):
    """Входные данные для запроса расписания на несколько дней"""

    classId: ClassVar[int] = 0x00000024
    class_id: Literal[0x00000024] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    session: str = Field(
        description="Строковый идентификатор сессии",
        min_length=1,
        max_length=64,
        pattern="[a-zA-Z0-9]+",
        examples=["55e5bccb595d10beb8d5bf85d447dff2c411275d3ce9f2823afb3a56407f8afe"]
    )
    before: int = Field(
        description="Количество дней расписания до сегодня",
        ge=0,
        le=14,
        examples=[7]
    )
    after: int = Field(
        description="Количество дней после сегодня",
        ge=1,
        le=21,
        examples=[14]
    )


class ScheduleApiRequest(ApiRequest):
    """Запрос расписания на несколько дней"""

    classId: ClassVar[int] = 0x00000023
    class_id: Literal[0x00000023] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: ScheduleInputData = Field(
        description="Данные сессии и период запрашиваемого расписания"
    )


class ScheduleHomeworkDocument(ApiBase):
    """Прикрепленный файл к домашнему заданию"""

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
    """Внеурочное занятие"""

    classId: ClassVar[int] = 0x0000000F
    class_id: Literal[0x0000000F] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    subject: str = Field(
        description="Название предмета внеурочного занятия",
        examples=["Математика"]
    )
    place: str = Field(
        description="Кабинет или другое место проведения внеурочного занятия",
        examples=["332"]
    )


class ScheduleHours(ApiBase):
    """Время проведения урока или внеурочного занятия"""

    classId: ClassVar[int] = 0x00000010
    class_id: Literal[0x00000010] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    start: str = Field(
        description="Начало урока или внеурочного занятия",
        examples=["08:00"]
    )
    end: str = Field(
        description="Окончание урока или внеурочного занятия",
        examples=["08:40"]
    )


class MarkLog(ApiBase):
    """Оценка или отметка посещаемости урока"""

    classId: ClassVar[int] = 0x00000016
    class_id: Literal[0x00000016] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    mood: Literal["good", "average", "bad", "more"] = Field(
        description="Тип оценки: хороший, средний, плохой или другой для отметок посещаемости",
        examples=["good"]
    )
    value: str = Field(
        description="Полученная оценка или отметка посещаемости",
        examples=["5"]
    )

    @staticmethod
    def moods() -> list[Literal["good", "average", "bad", "more"]]:
        return ["good", "average", "bad", "more"]

    @staticmethod
    def default_mood() -> Literal["good", "average", "bad", "more"]:
        return "more"

    @staticmethod
    def log_value(log_type: str) -> Optional[str]:
        match log_type:
            case "Absent":
                return "Н"  # Неявка
            case "Ill":
                return "Б"  # Болеет
            case "Late":
                return "О"  # Опоздал(а)
            case "Pass":
                return "П"  # Пропуск

        return None


class MarksOther(ApiBase):
    """Оценки другого ученика(цы) за тот жде урок"""

    classId: ClassVar[int] = 0x00000021
    class_id: Literal[0x00000021] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    name: str = Field(
        description="Имя и первая буква фамилия ученика(цы)"
    )
    marks: list[MarkLog] = Field(
        description="Оценки ученика(цы)"
    )


class ScheduleLesson0x00000011(ApiBase):
    """Урок устаревшая версия"""

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
        description="Дополнительные файлы к домашнему заданию"
    )


class ScheduleLesson(ApiBase):
    """Урок"""

    classId: ClassVar[int] = 0x00000017
    class_id: Literal[0x00000017] = Field(
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
    logs: list[MarkLog] = Field(
        description="Оценки и отметки посещаемости за урок"
    )
    othersMarks: list[MarksOther] = Field(
        description="Оценки других учеников за урок"
    )
    homework: Optional[str] = Field(
        description="Домашнее задание к уроку",
        examples=["Доделать классную работу"]
    )
    files: list[ScheduleHomeworkDocument] = Field(
        description="Дополнительные файлы к домашнему заданию"
    )


class ScheduleDay0x00000012(ApiBase):
    """День в расписании с уроками и внеурочными занятиями устаревшая версия"""

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
    lessons: list[ScheduleLesson0x00000011] = Field(
        description="Уроки в данный день"
    )
    hoursExtracurricularActivities: Optional[ScheduleHours] = Field(
        description="Часы проведения внеурочных занятий"
    )
    extracurricularActivities: list[ScheduleExtracurricularActivity] = Field(
        description="Внеурочные занятия в данный день"
    )


class ScheduleDay(ApiBase):
    """День в расписании с уроками и внеурочными занятиями"""

    classId: ClassVar[int] = 0x00000018
    class_id: Literal[0x00000018] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    date: str = Field(
        description="Дата дня в формате yyyy-MM-dd",
        examples=["2025-12-09"]
    )
    lessons: list[ScheduleLesson] = Field(
        description="Уроки в данный день"
    )
    hoursExtracurricularActivities: Optional[ScheduleHours] = Field(
        description="Часы проведения внеурочных занятий"
    )
    extracurricularActivities: list[ScheduleExtracurricularActivity] = Field(
        description="Внеурочные занятия в данный день"
    )


class ScheduleResult0x00000013(ApiBase):
    """Результат запроса расписания на 2 недели (15 дней) устаревшая версия"""

    classId: ClassVar[int] = 0x00000013
    class_id: Literal[0x00000013] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    schedule: list[ScheduleDay0x00000012] = Field(
        description="Расписание на 2 недели (15 дней)"
    )


class ScheduleResult0x00000019(ApiBase):
    """Результат запроса расписания на 3 недели (22 дня): 7 дней до сегодня, сегодня и 15 дней после устаревшая версия"""

    classId: ClassVar[int] = 0x00000019
    class_id: Literal[0x00000019] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    schedule: list[ScheduleDay] = Field(
        description="Расписание на 2 недели (15 дней)"
    )


class ScheduleResult(ApiBase):
    """Результат запроса расписания на несколько дней"""

    classId: ClassVar[int] = 0x00000026
    class_id: Literal[0x00000026] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    schedule: list[ScheduleDay] = Field(
        description="Расписание на несколько дней"
    )
    timezone: int = Field(
        description="Часовой пояс"
    )


class ScheduleApiResponse0x00000014(ApiResponse):
    """Ответ на запрос расписания на 2 недели (15 дней) устаревшая версия"""

    classId: ClassVar[int] = 0x00000014
    class_id: Literal[0x00000014] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ScheduleResult0x00000013] = Field(
        default=None,
        description="Данные о расписании на 2 недели (15 дней)"
    )


class ScheduleApiResponse0x00000020(ApiResponse):
    """Ответ на запрос расписания на 3 недели (22 дня): 7 дней до сегодня, сегодня и 15 дней после устаревшая версия"""

    classId: ClassVar[int] = 0x00000020
    class_id: Literal[0x00000020] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ScheduleResult0x00000019] = Field(
        default=None,
        description="Данные о расписании на 2 недели (15 дней)"
    )


class ScheduleApiResponse(ApiResponse):
    """Ответ на запрос расписания на несколько дней"""

    classId: ClassVar[int] = 0x00000027
    class_id: Literal[0x00000027] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ScheduleResult] = Field(
        default=None,
        description="Данные о расписании на несколько дней"
    )
