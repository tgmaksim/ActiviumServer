import datetime

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse

from pydantic import Field
from typing import ClassVar, Literal, Optional


__all__ = ['ScheduleHomeworkDocument', 'ScheduleExtracurricularActivity', 'ScheduleHours', 'WorkType', 'MarkLog',
           'MarksOther', 'ScheduleLesson', 'ScheduleDay', 'ScheduleResult', 'ScheduleApiResponse',
           'LessonRatingStatsResult', 'LessonRatingStatsApiResponse', 'MarkLast', 'MarksSubjectPeriod', 'MarksResult',
           'MarksApiResponse', 'MarksRatingStatsResult', 'MarksRatingStatsApiResponse', 'MarksSubjectRatingResult',
           'MarksSubjectRatingApiResponse', 'MarksSubjectFinal', 'MarksFinalResult', 'MarksFinalApiResponse']


class ScheduleHomeworkDocument(ApiBase):
    """Прикрепленный файл к домашнему заданию"""

    classId: ClassVar[int] = 0xA
    class_id: Literal[0xA] = Field(
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
    insideOpenUrl: Optional[str] = Field(
        description="Ссылка для открытия документа во внутреннем браузере приложения (прямая или через обработчик документов)",
        examples=["https://b1.csdnevnik.ru/file.docx"]
    )


class ScheduleHours(ApiBase):
    """Время проведения урока или внеурочного занятия"""

    classId: ClassVar[int] = 0xB
    class_id: Literal[0xB] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    start: datetime.datetime = Field(
        description="Начало урока или внеурочного занятия"
    )
    end: datetime.datetime = Field(
        description="Окончание урока или внеурочного занятия"
    )
    string: str = Field(
        description="Строковое представление времени провождения"
    )


class ScheduleExtracurricularActivity(ApiBase):
    """Внеурочное занятие"""

    classId: ClassVar[int] = 0xC
    class_id: Literal[0xC] = Field(
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
    hours: ScheduleHours = Field(
        description="Время проведения внеурочного занятия"
    )


class WorkType(ApiBase):
    """Тип работы на уроке"""

    classId: ClassVar[int] = 0xD
    class_id: Literal[0xD] = Field(
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
        return hash(self.abbr)


class MarkLog(ApiBase):
    """Оценка или отметка посещаемости урока"""

    classId: ClassVar[int] = 0xE
    class_id: Literal[0xE] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    mood: Literal["good", "average", "bad", "more"] = Field(
        description="Тип оценки: хороший, средний, плохой или другой (для отметок посещаемости)",
        examples=["good"]
    )
    value: str = Field(
        description="Полученная оценка или отметка посещаемости",
        examples=["5", "П", "ОСВ"]
    )
    work: Optional[WorkType] = Field(
        description="Тип работы, за что получена оценка"
    )
    created: Optional[datetime.datetime] = Field(
        description="Дата и время выставления оценки"
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


class MarksOther(ApiBase):
    """Оценки другого ученика(цы) за тот жде урок"""

    classId: ClassVar[int] = 0xF
    class_id: Literal[0xF] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    number: Optional[int] = Field(
        default=None,
        description="Место в рейтинге"
    )
    name: str = Field(
        description="Имя и первая буква фамилия ученика(цы)"
    )
    marks: list[MarkLog] = Field(
        description="Оценки ученика(цы)"
    )


class ScheduleLesson(ApiBase):
    """Урок"""

    classId: ClassVar[int] = 0x10
    class_id: Literal[0x10] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    lessonKey: str = Field(
        description="Ключ для создания заметок к уроку и отправки похвалы",
        pattern=r'[0-9a-z]{1,13}',
        min_length=1,
        max_length=13
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
        examples=["332", "спортивный зал"]
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
    avgGroupLessonMark: Optional[MarkLog] = Field(
        description="Средний балл оценок за урок в классе"
    )
    homework: Optional[str] = Field(
        description="Домашнее задание к уроку",
        examples=["Доделать классную работу"]
    )
    note: Optional[str] = Field(
        description="Заметка к уроку",
        examples=["Сделать прошлую домашнюю работу"]
    )
    files: list[ScheduleHomeworkDocument] = Field(
        description="Дополнительные файлы к домашнему заданию"
    )
    ratingKey: Optional[str] = Field(
        description="Ключ для получения дополнительной информации по оценкам",
        pattern=r'[0-9a-z]{1,13}\.[0-9a-z]{1,13}\.\d{4}-\d{2}-\d{2}',
        min_length=9,
        max_length=38
    )


class ScheduleDay(ApiBase):
    """День в расписании с уроками и внеурочными занятиями"""

    classId: ClassVar[int] = 0x11
    class_id: Literal[0x11] = Field(
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
    ea: list[ScheduleExtracurricularActivity] = Field(
        description="Внеурочные занятия в данный день"
    )


class ScheduleResult(ApiBase):
    """Результат запроса расписания на несколько дней"""

    classId: ClassVar[int] = 0x12
    class_id: Literal[0x12] = Field(
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
    hasAbilityPraise: bool = Field(
        description="Можно ли отправить похвалу ребенку от родителя"
    )


class ScheduleApiResponse(ApiResponse):
    """Ответ на запрос расписания на несколько дней"""

    classId: ClassVar[int] = 0x13
    class_id: Literal[0x13, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[ScheduleResult] = Field(
        default=None,
        description="Данные о расписании на несколько дней"
    )


class LessonRatingStatsResult(ApiBase):
    """Результат запроса получения дополнительной статистики по оценкам на уроке"""

    classId: ClassVar[int] = 0x14
    class_id: Literal[0x14] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    oldAvgMark: Optional[MarkLog] = Field(
        description="Средний балл до получения оценок в день урока"
    )
    newAvgMark: Optional[MarkLog] = Field(
        description="Средний балл после получения оценок в день урока"
    )


class LessonRatingStatsApiResponse(ApiResponse):
    """Ответ на запрос получения дополнительной статистики по оценкам на уроке"""

    classId: ClassVar[int] = 0x15
    class_id: Literal[0x15, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[LessonRatingStatsResult] = Field(
        default=None,
        description="Дополнительная статистика по оценкам на уроке"
    )


class MarkLast(ApiBase):
    """Оценка с рейтингом"""

    classId: ClassVar[int] = 0x16
    class_id: Literal[0x16] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    mark: MarkLog = Field(
        description="Полученная оценка"
    )
    subject: str = Field(
        description="Название предмета, по которому получена оценка",
        examples=["Математика"]
    )
    lessonDate: Optional[datetime.date] = Field(
        description="Дата урока, на котором поставлена оценка"
    )
    humanLessonDate: Optional[str] = Field(
        description="Дата урока в формате '%e %b.' для показа пользователю",
        examples=["9 дек."]
    )
    ratingKey: str = Field(
        description="Ключ для получения оценок в классе за тот же урок",
        pattern=r'[wl][0-9a-z]{1,13}',
        min_length=2,
        max_length=14
    )


class MarksSubjectPeriod(ApiBase):
    """Оценки по предмету в отчетном периоде"""

    classId: ClassVar[int] = 0x17
    class_id: Literal[0x17] = Field(
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
    ratingKey: str = Field(
        description="Ключ для получения рейтинга в классе по предмету",
        pattern=r'[0-9a-z]{1,13}\.[0-9a-z]{1,13}',
        min_length=3,
        max_length=27
    )


class MarksResult(ApiBase):
    """Результат запроса получения оценок последних и по предметам"""

    classId: ClassVar[int] = 0x18
    class_id: Literal[0x18] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    recentMarks: list[MarkLast] = Field(
        description="Последние оценки по дате выставления за последнюю неделю"
    )
    periodMarks: list[MarksSubjectPeriod] = Field(
        description="Оценки по предметам за текущий отчетный период"
    )
    ratingKey: str = Field(
        description="Ключ для получения общего рейтинга в классе",
        pattern=r'[0-9a-z]{1,13}',
        min_length=1,
        max_length=13
    )


class MarksApiResponse(ApiResponse):
    """Ответ на запрос получения оценок последних и по предметам"""

    classId: ClassVar[int] = 0x19
    class_id: Literal[0x19, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[MarksResult] = Field(
        default=None,
        description="Оценки последние и по предметам"
    )


class MarksRatingStatsResult(ApiBase):
    """Результат запроса получения дополнительной статистики по последней оценке"""

    classId: ClassVar[int] = 0x1A
    class_id: Literal[0x1A] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    othersMarks: list[MarksOther] = Field(
        description="Оценки класса за тот же урок"
    )
    avgGroupMark: Optional[MarkLog] = Field(
        description="Средний балл оценок за урок в классе"
    )
    oldAvgMark: Optional[MarkLog] = Field(
        description="Средний балл до получения оценок в день урока"
    )
    newAvgMark: Optional[MarkLog] = Field(
        description="Средний балл после получения оценок в день урока"
    )


class MarksRatingStatsApiResponse(ApiResponse):
    """Ответ на запрос получения дополнительной статистики по последней оценке"""

    classId: ClassVar[int] = 0x1B
    class_id: Literal[0x1B, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[MarksRatingStatsResult] = Field(
        default=None,
        description="Дополнительная статистика по последней оценке"
    )


class MarksSubjectRatingResult(ApiBase):
    """Результат запроса получения общего или предметного рейтинга"""

    classId: ClassVar[int] = 0x1C
    class_id: Literal[0x1C] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    rating: list[MarksOther] = Field(
        description="Средние баллы одноклассников"
    )
    oldMark: Optional[MarksOther] = Field(
        description="Прошлая оценка с момента прошлого запроса"
    )


class MarksSubjectRatingApiResponse(ApiResponse):
    """Ответ на запрос получения общего или предметного рейтинга"""

    classId: ClassVar[int] = 0x1D
    class_id: Literal[0x1D, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[MarksSubjectRatingResult] = Field(
        default=None,
        description="Рейтинг в классе и прошлое место в рейтинге"
    )


class MarksSubjectFinal(ApiBase):
    """Оценки по предмету за отчетные периоды и за год"""

    classId: ClassVar[int] = 0x1E
    class_id: Literal[0x1E] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    subject: str = Field(
        description="Название предмета",
        examples=["Математика"]
    )
    marks: list[Optional[MarkLog]] = Field(
        description="Оценки по предмету в порядке отчетных периодов"
    )
    finalMark: Optional[MarkLog] = Field(
        description="Итоговая оценка за год по предмету"
    )


class MarksFinalResult(ApiBase):
    """Результат запроса получения оценок за период и за год"""

    classId: ClassVar[int] = 0x1F
    class_id: Literal[0x1F] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    countPeriods: int = Field(
        description="Количество отчетных периодов"
    )
    finalMarks: list[MarksSubjectFinal] = Field(
        description="Оценки по предметам за отчетные периоды и за год"
    )


class MarksFinalApiResponse(ApiResponse):
    """Ответ на запрос получения оценок за период и за год"""

    classId: ClassVar[int] = 0x20
    class_id: Literal[0x20, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[MarksFinalResult] = Field(
        default=None,
        description="Оценки по предметам за отчетные периоды и за год"
    )
