import datetime

from pydantic import Field
from typing import Optional, ClassVar, Literal

from api.entities import ApiBase, ApiSession, ApiRequest, ApiResponse


__all__ = ['ScheduleApiRequest0x0000000D', 'ScheduleApiRequest0x00000015', 'ScheduleApiRequest0x00000022',
           'ScheduleInputData', 'ScheduleApiRequest0x00000023', 'ScheduleApiRequest',

           'ScheduleHomeworkDocument', 'ScheduleExtracurricularActivity', 'ScheduleHours', 'WorkType',
           'MarkLog0x00000016', 'MarkLog', 'MarksOther0x00000021', 'MarksOther', 'ScheduleLesson0x00000011',
           'ScheduleLesson0x00000017', 'ScheduleLesson', 'ScheduleDay0x00000012', 'ScheduleDay0x00000018',
           'ScheduleDay',

           'ScheduleResult0x00000013', 'ScheduleResult0x00000019', 'ScheduleResult0x00000026', 'ScheduleResult',
           'ScheduleApiResponse0x00000014', 'ScheduleApiResponse0x00000020', 'ScheduleApiResponse0x00000027',
           'ScheduleApiResponse',

           'MarksApiRequest', 'MarkLast', 'MarksSubjectPeriod', 'MarksResult', 'MarksApiResponse']


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


class ScheduleApiRequest0x00000023(ApiRequest):
    """Запрос расписания на несколько дней устаревшая версия"""

    classId: ClassVar[int] = 0x00000023
    class_id: Literal[0x00000023] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: ScheduleInputData = Field(
        description="Данные сессии и период запрашиваемого расписания"
    )

class ScheduleApiRequest(ApiRequest):
    """Запрос расписания на несколько дней"""

    classId: ClassVar[int] = 0x00000028
    class_id: Literal[0x00000028] = Field(
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


class WorkType(ApiBase):
    """Тип работы на уроке"""

    classId: ClassVar[int] = 0x00000029
    class_id: Literal[0x00000029] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    title: str = Field(
        description="Название типа работы",
        examples=["Контрольная работа"]
    )
    abbr: str = Field(
        description="Аббревиатура типа работы",
        examples=["КР"]
    )

    def __hash__(self):
        return hash(self.title)


class MarkLog0x00000016(ApiBase):
    """Оценка или отметка посещаемости урока устаревшая версия"""

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

    moods: ClassVar[list[str]] = ["good", "average", "bad", "more"]

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


class MarkLog(ApiBase):
    """Оценка или отметка посещаемости урока"""

    classId: ClassVar[int] = 0x0000002A
    class_id: Literal[0x0000002A] = Field(
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
    work: Optional[WorkType] = Field(
        description="Тип работы, за что получена оценка"
    )

    moods: ClassVar[list[str]] = ["good", "average", "bad", "more"]

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


class MarksOther0x00000021(ApiBase):
    """Оценки другого ученика(цы) за тот жде урок устаревшая версия"""

    classId: ClassVar[int] = 0x00000021
    class_id: Literal[0x00000021] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    name: str = Field(
        description="Имя и первая буква фамилия ученика(цы)"
    )
    marks: list[MarkLog0x00000016] = Field(
        description="Оценки ученика(цы)"
    )


class MarksOther(ApiBase):
    """Оценки другого ученика(цы) за тот жде урок"""

    classId: ClassVar[int] = 0x0000002B
    class_id: Literal[0x0000002B] = Field(
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


class ScheduleLesson0x00000017(ApiBase):
    """Урок устаревшая версия"""

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
    logs: list[MarkLog0x00000016] = Field(
        description="Оценки и отметки посещаемости за урок"
    )
    othersMarks: list[MarksOther0x00000021] = Field(
        description="Оценки других учеников за урок"
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

    classId: ClassVar[int] = 0x0000002C
    class_id: Literal[0x0000002C] = Field(
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
    works: list[WorkType] = Field(
        description="Типы работ на уроке"
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

    date: datetime.date = Field(
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


class ScheduleDay0x00000018(ApiBase):
    """День в расписании с уроками и внеурочными занятиями"""

    classId: ClassVar[int] = 0x00000018
    class_id: Literal[0x00000018] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    date: datetime.date = Field(
        description="Дата дня в формате ISO"
    )
    lessons: list[ScheduleLesson0x00000017] = Field(
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

    classId: ClassVar[int] = 0x0000002D
    class_id: Literal[0x0000002D] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    date: datetime.date = Field(
        description="Дата дня в формате ISO"
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

    schedule: list[ScheduleDay0x00000018] = Field(
        description="Расписание на 2 недели (15 дней)"
    )


class ScheduleResult0x00000026(ApiBase):
    """Результат запроса расписания на несколько дней"""

    classId: ClassVar[int] = 0x00000026
    class_id: Literal[0x00000026] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    schedule: list[ScheduleDay0x00000018] = Field(
        description="Расписание на несколько дней"
    )
    timezone: int = Field(
        description="Часовой пояс"
    )


class ScheduleResult(ApiBase):
    """Результат запроса расписания на несколько дней"""

    classId: ClassVar[int] = 0x0000002E
    class_id: Literal[0x0000002E] = Field(
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


class ScheduleApiResponse0x00000027(ApiResponse):
    """Ответ на запрос расписания на несколько дней устаревшая версия"""

    classId: ClassVar[int] = 0x00000027
    class_id: Literal[0x00000027] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ScheduleResult0x00000026] = Field(
        default=None,
        description="Данные о расписании на несколько дней"
    )


class ScheduleApiResponse(ApiResponse):
    """Ответ на запрос расписания на несколько дней"""

    classId: ClassVar[int] = 0x0000002F
    class_id: Literal[0x0000002F] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ScheduleResult] = Field(
        default=None,
        description="Данные о расписании на несколько дней"
    )


class MarksApiRequest(ApiRequest):
    """Запрос оценок: последних по дате выставления, текущих и итоговых по предметам"""

    classId: ClassVar[int] = 0x00000030
    class_id: Literal[0x00000030] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    data: ApiSession = Field(
        description="Данные сессии"
    )


class MarkLast(ApiBase):
    """Оценка с рейтингом"""

    classId: ClassVar[int] = 0x00000031
    class_id: Literal[0x00000031] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    mark: MarkLog = Field(
        description="Полученная оценка"
    )
    work: Optional[WorkType] = Field(
        description="Тип работы, за что получена оценка"
    )
    subject: str = Field(
        description="Название предмета, по которому получена оценка",
        examples=["Математика"]
    )
    sentDatetime: datetime.datetime = Field(
        description="Дата и время выставления оценки в формате ISO"
    )
    lessonDate: Optional[datetime.date] = Field(
        description="Дата урока в формате ISO"
    )
    lessonDateFormat: Optional[str] = Field(
        description="Дата урока в формате %e %b. для показа пользователю",
        examples=["9 дек."]
    )
    othersMarks: list[MarksOther] = Field(
        description="Оценки других учеников за тот же урок"
    )


class MarksSubjectPeriod(ApiBase):
    """Оценки по предмету в отчетном периоде"""

    classId: ClassVar[int] = 0x00000035
    class_id: Literal[0x00000035] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    subject: str = Field(
        description="Название предмета",
        examples=["Математика"]
    )
    marks: list[MarkLog] = Field(
        description="Оценки по предмету в порядке даты выставления"
    )
    averageMark: Optional[MarkLog] = Field(
        description="Средний балл оценок по предмету с точностью до 2 знаков после запятой"
    )
    periodMark: Optional[MarkLog] = Field(
        description="Оценка за отчетный период по предмету"
    )
    othersAverageMark: list[MarksOther] = Field(
        description="Средний балл по предмету класса"
    )


class MarksResult(ApiBase):
    """Результат запроса оценок: последних по дате выставления, текущих итоговых по предметам"""

    classId: ClassVar[int] = 0x00000032
    class_id: Literal[0x00000032] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    lastMarks: list[MarkLast] = Field(
        description="Последние оценки по дате выставления"
    )
    periodMarks: list[MarksSubjectPeriod] = Field(
        description="Оценки по предметам в текущем отчетном периоде"
    )
    classRating: list[MarksOther] = Field(
        description="Средние баллы по всем предметам в совокупности"
    )


class MarksApiResponse(ApiResponse):
    """Ответ на запрос оценок: последних по дате выставления, текущих и итоговых по предметам"""

    classId: ClassVar[int] = 0x00000033
    class_id: Literal[0x00000033] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[MarksResult] = Field(
        default=None,
        description="Оценки: последние по дате выставления, текущие и итоговые по предметам"
    )
