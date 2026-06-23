import re

from statistics import median, mean

from asyncio import gather
from typing import Callable, Optional, Literal, Union

from yarl import URL
from httpx import AsyncClient
from datetime import datetime, timedelta, time, date, UTC

from dnevnikru.exceptions import BaseDnevnikruException
from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi
from ..repositories.lesson_note_repository import LessonNoteRepository
from ..repositories.school_post_like_repository import SchoolPostLikeRepository
from ..repositories.school_post_repository import SchoolPostRepository
from ..repositories.school_post_vision_repository import SchoolPostVisionRepository

from ..schemas.school_schemas import SchoolPost
from ..schemas.dnevnik_tools_schemas import Note

from ...config.project_config import settings
from ...dependencies.auth import check_session
from ...utils.zip_int import zip_int, unzip_int
from ...dependencies.httpx import get_httpx_client
from ...utils.datetime import datetime_now, astimezone
from ...repositories.statistic_repository import StatName

from ...models import LessonNote
from ...models.hour_model import Hour
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ..repositories.cache_repository import CacheRepository
from ..repositories.highlighting_person_repository import HighlightingPersonRepository
from ..repositories.extracurricular_activity_repository import ExtracurricularActivityRepository

from ...models.child_model import Child
from ...models.parent_model import Parent
from ...models.session_model import Session
from ...schemas.error_schema import ApiError
from ...api.session_error import SessionError
from ..schemas.dnevnik_schemas import (
    MarkLog,
    MarkLast,
    WorkType,
    MarksOther,
    ScheduleDay,
    MarksResult,
    ScheduleHours,
    ScheduleLesson,
    ScheduleResult,
    ScheduleDay0x11,
    MarksApiResponse,
    MarksFinalResult,
    MarksSubjectFinal,
    MarksSubjectPeriod,
    ScheduleResult0x12,
    ScheduleLesson0x10,
    ScheduleApiResponse,
    MarksFinalApiResponse,
    MarksRatingStatsResult,
    ScheduleApiResponse0x13,
    LessonRatingStatsResult,
    ScheduleHomeworkDocument,
    MarksSubjectRatingResult,
    MarksRatingStatsResult0x1A,
    MarksRatingStatsApiResponse,
    LessonRatingStatsApiResponse,
    MarksSubjectRatingApiResponse,
    MarksRatingStatsApiResponse0x1B,
    ScheduleExtracurricularActivity,
)


__all__ = ['DnevnikService']

# Дневник.ру не отправляет mark_type для среднего балла, поэтому выбирается mark5
mark5_moods: dict[int, Literal["good", "average", "bad"]] = {
    5: "good",
    4: "good",
    3: "average",
    2: "bad",
    1: "bad"
}


def round_or_int(number: float) -> Union[int, float]:
    result = round(number, 2)

    if result == int(result):
        return int(result)
    return result


class DnevnikService(BaseService[AppUnitOfWork]):
    """Сервис для взаимодействия с расписанием, оценками и другими данными Дневника.ру"""

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def getSchedule(self, session_id: str, before: int, after: int, api: int = None) -> Union[ScheduleApiResponse0x13, ScheduleApiResponse]:
        if api == 1:
            answer_type = ScheduleApiResponse
            result_type = ScheduleResult
        else:
            answer_type = ScheduleApiResponse0x13
            result_type = ScheduleResult0x12

        async with self.uow_factory() as uow:
            if after + before > 30:
                await uow.log_repository.add_log(
                    path='getSchedule',
                    session_id=session_id,
                    status=False,
                    value=f"IntervalTooLong: {after} + {before} = {after + before}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="IntervalTooLong",
                        errorMessage=f"Максимальный размер интервала равен 30 дням ({after + before} дней запрошено)"
                    )
                )

            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            dnr = AioDnevnikruApi(get_httpx_client(), session.dnevnik_token)

            # Границы интервала запрашиваемого расписания
            now = datetime_now(child.timezone)

            start = (now - timedelta(days=before)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = start.date()

            end = (now + timedelta(days=after)).replace(hour=23, minute=59, second=59, microsecond=99999)
            end_date = end.date()

            # Показывать только открытые заметки для родителя
            only_public_notes = parent.parent_id != child.child_id

            person_schedule: dict  # Расписание конкретно для обучающегося
            files: dict[int, list[ScheduleHomeworkDocument]]  # Файлы к домашнему заданию по идентификаторам уроков
            notes: dict[int, LessonNote]  # Заметки к урокам в расписании
            marks: dict[int, list[MarkLog]]  # Оценки по урокам
            others_marks: dict[int, list[MarksOther]]  # Оценки класса по урокам и обучающимся
            active_period: dict  # Текущий отчетный период
            ea: dict[date, list[ScheduleExtracurricularActivity]]  # Внеурочные занятия по дням
            school_hours: list[Hour]  # Дополнительное звонковое расписание, отличное от Дневника.ру
            posts: dict[date, list[SchoolPost]]  # Посты с мероприятиями по дате
            my_likes: list[int]  # Посты с реакцией пользователя
            my_visions: list[int]  # Посты, которые были увидены

            # Одновременные запросы к Дневнику.ру и БД для получения всех необходимых независимых данных
            try:
                (person_schedule, files, notes), (marks, others_marks), active_period, ea, school_hours, (posts, my_likes, my_visions) = await gather(
                    self._get_person_schedule_with_homeworks_and_notes(
                        uow.lesson_note_repository,
                        dnr,
                        child,
                        start_date,
                        end_date,
                        only_public_notes
                    ),
                    self._get_schedule_marks(
                        uow.cache_repository,
                        dnr,
                        uow.highlighting_person_repository,
                        session,
                        child,
                        start_date,
                        end_date
                    ),
                    self._get_period(
                        uow.cache_repository,
                        dnr,
                        session,
                        child,
                        now.date()
                    ),
                    self._get_extracurricular_activities(
                        uow.extracurricular_activity_repository,
                        child,
                        (start, end)
                    ),
                    uow.hour_repository.get_school_hours(child.school_id),
                    self._get_schedule_posts(
                        uow.school_post_repository,
                        uow.school_post_like_repository,
                        uow.school_post_vision_repository,
                        child,
                        session,
                        (start_date, end_date)
                    )
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            # Обработка полученных данных
            result = self._get_schedule_result(
                child,
                api,
                person_schedule, school_hours, notes, active_period,
                files, ea,
                posts, my_likes, my_visions,
                marks, others_marks
            )

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getSchedule)

            return answer_type(
                answer=result_type(
                    schedule=result,
                    timezone=child.timezone,
                    hasAbilityPraise=parent.parent_id != child.child_id
                )
            )

    @classmethod
    def _get_schedule_result(
            cls,
            child: Child,
            api: Optional[int],
            person_schedule: dict, school_hours: list[Hour], notes: dict[int, LessonNote], active_period: dict,
            files: dict[int, list[ScheduleHomeworkDocument]], ea: dict[date, list[ScheduleExtracurricularActivity]],
            posts: dict[date, list[SchoolPost]], my_likes: list[int], my_visions: list[int],
            marks: dict[int, list[MarkLog]], others_marks: dict[int, list[MarksOther]]
    ) -> list[Union[ScheduleDay, ScheduleDay0x11]]:
        """Обработка полученных данных для создания расписания"""

        if api == 1:
            day_type = ScheduleDay
            lesson_type = ScheduleLesson
        else:
            day_type = ScheduleDay0x11
            lesson_type = ScheduleLesson0x10

        posts_by_date = {
            post_date: [
                SchoolPost(
                    postId=post.post_id,
                    title=post.title,
                    description=post.description,
                    imageUrl=str(URL(settings.URL).joinpath(
                        'school', 'posts', str(post.post_id), 'image.jpg'
                    )) if post.has_image else None,
                    author=post.author,
                    authorVerified=post.author_verified,
                    scheduleDate=post.schedule_date,
                    humanScheduleDate=post.schedule_date and post.schedule_date.strftime('%e %b.').strip(),
                    isUpdated=post.is_updated,
                    countViewings=post.count_viewings,
                    countLikes=post.count_likes,
                    hasMyLike=post.post_id in my_likes,
                    isSaw=post.post_id in my_visions,
                    createdAt=post.created_at,
                    humanCreatedAt=astimezone(post.created_at, post.timezone).strftime('%e %b. в %H:%M').strip(),
                    postUrl=str(URL(settings.URL).joinpath('school', 'posts', str(post.post_id)))
                )
                for post in day_posts
            ]
            for post_date, day_posts in posts.items()
        }

        result = []
        for day in sorted(person_schedule['days'], key=lambda d: datetime.fromisoformat(d['date'])):
            subjects = {subject['id']: subject['name'] for subject in day['subjects']}
            works = {work['id']: work for work in day['works']}
            work_types = {work_type['id']: work_type for work_type in day['workTypes']}

            # Текст домашних заданий по идентификаторам уроков
            homeworks: dict[int, list[str]] = {}
            for homework in day['homeworks']:
                if homeworks.get(homework['lesson']) is None:
                    homeworks[homework['lesson']] = []
                homeworks[homework['lesson']].append(homework['text'])

            # Отметки о посещаемости на уроках
            logs = {
                lesson_log['lesson']: [
                    MarkLog(
                        mood=MarkLog.default_mood(),
                        value=value,
                        work=None,
                        created=astimezone(
                            datetime.fromisoformat(lesson_log['createdDate']).replace(tzinfo=UTC),
                            child.timezone
                        )
                    )
                ] for lesson_log in day['lessonLogEntries']
                if (value := MarkLog.log_value(lesson_log['status']))
            }

            day_date = datetime.fromisoformat(day['date'])

            # Звонковое расписание, отличное от Дневника.ру
            hours: Optional[Hour] = None
            for hour in school_hours:
                if day_date.month in hour.months and day_date.weekday() in hour.weekdays:
                    hours = hour
                    break

            lessons = []
            for lesson in sorted(day['lessons'], key=lambda l: l['number']):
                # Оценки пользователя и одноклассников
                lesson_marks = marks.get(lesson['id'], [])
                lesson_others_marks = others_marks.get(lesson['id'], [])

                # Типы работ всех оценок на уроке
                mark: MarkLog
                log_works = {mark.work for mark in lesson_marks}
                log_works.update(*({mark.work for mark in other_marks.marks} for other_marks in lesson_others_marks))

                # Типы работ, привязанные к уроку, кроме работы по умолчанию
                lesson_works = {
                    WorkType(
                        title=work_type['name'],
                        abbr=work_type['abbreviation']
                    )
                    for work_id in lesson['works']
                    if (work_type := work_types.get(works.get(work_id, {}).get('workType')))
                       and work_type['kind'] != 'DefaultNewLessonWork'
                }

                # Время урока
                if hours and len(hours.hours) >= lesson['number']:
                    start = time.fromisoformat(hours.hours[lesson['number'] - 1]['start'])
                    end = time.fromisoformat(hours.hours[lesson['number'] - 1]['end'])
                    string = hours.hours[lesson['number'] - 1]['string']
                else:
                    start = time.fromisoformat(lesson['hours'].split(' - ')[0])
                    end = time.fromisoformat(lesson['hours'].split(' - ')[1])
                    string = lesson['hours']
                lesson_hours = ScheduleHours(
                    start=astimezone(day_date.replace(hour=start.hour, minute=start.minute), child.timezone),
                    end=astimezone(day_date.replace(hour=end.hour, minute=end.minute), child.timezone),
                    string=string
                )

                # Средний балл всех оценок на уроке
                avg = cls._calc_avg(lesson_marks, lesson_others_marks)

                lesson_key = zip_int(lesson['id'])

                # Заметка к уроку, если есть
                if note := notes.get(lesson['id']):
                    if api == 1:
                        lesson_note = Note(
                            lessonKey=lesson_key,
                            text=note.text,
                            public=note.public,
                            remindTime=note.remind_time and astimezone(note.remind_time, child.timezone)
                        )
                    else:
                        lesson_note = note.text
                else:
                    lesson_note = None

                lessons.append(lesson_type(
                    lessonKey=lesson_key,
                    number=lesson['number'] - 1,  # Начало с 0, а не с 1, как в Дневнике.ру
                    subject=subjects.get(lesson['subjectId'], "Неизвестный предмет"),
                    place=lesson['place'],
                    works=list(lesson_works.union(log_works)),  # Объединение множеств с типами работ
                    hours=lesson_hours,
                    logs=lesson_marks + logs.get(lesson['id'], []),
                    othersMarks=lesson_others_marks,
                    avgGroupLessonMark=avg,
                    homework='; '.join(homeworks.get(lesson['id'], [])) or None,
                    note=lesson_note,
                    files=files.get(lesson['id'], []),
                    ratingKey=f"{zip_int(active_period['id'])}.{zip_int(lesson['subjectId'])}.{day_date.date()}",
                    dnevnikruUrl=cls._get_lesson_url(child.school_id, lesson['id'])
                ))

            result.append(day_type(
                date=day_date.date(),
                lessons=lessons,
                ea=ea.get(day_date.date(), []),
                schoolPosts=posts_by_date.get(day_date.date(), [])  # Для ScheduleDay0x11 игнорируется
            ))

        return result

    @classmethod
    async def _get_person_schedule_with_homeworks_and_notes(
            cls, lesson_note_repository: LessonNoteRepository, dnr: AioDnevnikruApi,
            child: Child,
            start_date: date, end_date: date, only_public_notes: bool
    ) -> tuple[dict, dict[int, list[ScheduleHomeworkDocument]], dict[int, LessonNote]]:
        """
        Получение расписания для пользователя, файлов к домашним заданиям и заметок к урокам

        :param lesson_note_repository: LessonNoteRepository для получения заметок к урокам
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param child: ребенок (профиль), для которого требуется расписание
        :param start_date: начала периода расписания
        :param end_date: конец периода расписания
        :param only_public_notes: получить только открытые заметки к урокам (для родителя)
        :return: расписание для пользователя, файлы к домашним заданиям по идентификаторам уроков,
        заметки по идентификаторам уроков
        """

        schedule = await dnr.get_person_schedule(child.child_id, child.group_id, start_date, end_date)

        # Идентификаторы всех уроков и домашних заданий
        lessons_id = []
        homeworks_id = []
        for day in schedule['days']:
            for homework in day['homeworks']:
                homeworks_id.append(homework['id'])
            for lesson in day['lessons']:
                lessons_id.append(lesson['id'])

        # Получение полной информации о домашних заданиях и заметок к урокам по их идентификаторам
        homeworks, notes = await gather(
            cls._get_homeworks_files(dnr, homeworks_id=homeworks_id),
            lesson_note_repository.get_notes(child.child_id, lessons_id, only_public=only_public_notes)
        )

        homework_documents = {
            lessons_id[i]: files
            for i, homework_id in enumerate(homeworks_id)
            if (files := homeworks.get(homework_id)) is not None
        }

        return schedule, homework_documents, notes

    @classmethod
    async def _get_homeworks_files(
            cls, dnr: AioDnevnikruApi,
            homeworks_id: list[int]
    ) -> dict[int, list[ScheduleHomeworkDocument]]:
        """
        Получение файлов к домашним заданиям по идентификаторам

        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param homeworks_id: идентификаторы домашних заданий
        :return: файлы к домашним заданиям по идентификаторам домашних заданий
        """

        if not homeworks_id:
            return {}

        homeworks = await dnr.get_homeworks(homeworks_id)

        results = {}
        files = {file['id']: file for file in homeworks['files']}

        for homework in homeworks['works']:
            for file_id in homework['files']:
                if results.get(homework['id']) is None:
                    results[homework['id']] = []

                file = files[file_id]
                results[homework['id']].append(ScheduleHomeworkDocument(
                    fileName=f"{file['name']}.{file['type'].lower()}",
                    downloadUrl=file['downloadUrl']
                ))

        return results

    @classmethod
    async def _get_schedule_marks(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            highlighting_person_repository: HighlightingPersonRepository,
            session: Session, child: Child,
            start_date: date, end_date: date
    ) -> tuple[dict[int, list[MarkLog]], dict[int, list[MarksOther]]]:
        """
        Получение оценок в расписании

        :param cache_repository: CacheRepository для получения кэша типов работ и имен одноклассников
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param highlighting_person_repository: HighlightingPersonRepository для получения правил сортировки оценок
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются оценки
        :param start_date: начало периода расписания
        :param end_date: конец периода расписания
        :return: оценки пользователя по идентификаторам уроков, оценки одноклассников по идентификаторам уроков
        """

        my_marks = {}
        others_marks = {}

        # Оценки всей учебной группы (класса) за период
        marks = await dnr.get_group_marks(child.group_id, start_date, end_date)

        work_types_id: set[int] = set()
        persons_id: set[int] = set()
        for mark in marks:
            work_types_id.add(mark['workType'])
            persons_id.add(mark['person'])

        # Одновременное получение названий типов работ, имен одноклассников, выделенных одноклассников
        work_types, persons, _highlighting_persons = await gather(
            cls._get_work_types(cache_repository, dnr, session, child, work_types_id),
            cls._get_persons_name(cache_repository, dnr, session, child, persons_id),
            highlighting_person_repository.get_highlighting_persons(session.parent_id)
        )

        highlighting_persons = {person.person_id for person in _highlighting_persons}

        for mark in marks:
            mood = mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood()

            # Оценка текущего ребенка (профиля)
            if mark['person'] == child.child_id:
                if my_marks.get(mark['lesson']) is None:
                    my_marks[mark['lesson']] = []

                my_marks[mark['lesson']].append(MarkLog(
                    mood=mood,
                    value=mark['textValue'],
                    work=work_types.get(mark['workType']),
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                ))
            # Оценка одноклассника
            else:
                if others_marks.get(mark['lesson']) is None:
                    others_marks[mark['lesson']] = {}
                if others_marks[mark['lesson']].get(mark['person']) is None:
                    if persons.get(mark['person']) is None:
                        continue
                    others_marks[mark['lesson']][mark['person']] = MarksOther(
                        name=persons[mark['person']],
                        personKey=zip_int(mark['person']),
                        isHighlighting=mark['person'] in highlighting_persons,
                        marks=[]
                    )

                other = others_marks[mark['lesson']][mark['person']]
                other.marks.append(MarkLog(
                    value=mark['textValue'],
                    mood=mood,
                    work=work_types.get(mark['workType']),
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                ))

        # Сортировка одноклассников по оценке и наличию выделения
        others_marks = {
            lesson_id: sorted(
                others_marks[lesson_id].values(),
                key=cls._key_others_marks,
                reverse=True
            )
            for lesson_id in others_marks
        }

        return my_marks, others_marks

    @classmethod
    def _key_others_marks(cls, other_marks: MarksOther):
        """
        Функция-ключ для сортировки оценок одноклассников по правилам

        1. Есть ли выделение
        2. Средний балл всех оценок
        3. Каждая оценка
        4. Имя одноклассника
        """

        marks: list[float] = []
        for _mark in other_marks.marks:
            mark = _mark.value.replace(',', '.')

            pm = 0
            if '+' in mark:  # Плюс учитывается как +0.25 балла
                mark = mark.replace('+', '')
                pm = +0.25
            elif '-' in mark:  # Минус учитывается как -0.25 балла
                mark = mark.replace('-', '')
                pm = -0.25

            if mark.isnumeric():
                marks.append(float(mark) + pm)

        if len(marks) == 0:
            return other_marks.isHighlighting, 0, [], other_marks.name
        return other_marks.isHighlighting, sum(marks) / len(marks), marks, other_marks.name

    @classmethod
    async def _get_work_types(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            work_types_id: set[int]
    ) -> dict[int, WorkType]:
        """
        Получение типов работ по идентификаторам

        :param cache_repository: CacheRepository для получения типов работ из кэша, если записаны
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуется получить типы работ
        :param work_types_id: идентификаторы необходимых типов работ на уроке
        :return: типы работ по идентификаторам
        """

        if not work_types_id:
            return {}

        # Получение типов работ из кэша
        work_types_key = [f"workType|{work_type_id}" for work_type_id in work_types_id]
        caches = await cache_repository.get_caches(session.session_id, child.child_id, work_types_key)
        results = {
            int(cache.key.split("|")[1]): WorkType(
                title=cache.value['title'],
                abbr=cache.value['abbr']
            )
            for cache in caches
        }

        # Если из кэша все необходимые типы работ получены
        if work_types_id == results.keys():
            return results

        # Иначе запрос к Дневнику.ру
        work_types = await dnr.get_work_types(child.school_id)

        new_caches = []

        for work_type in work_types:
            new_caches.append((
                f"workType|{work_type['id']}",
                {
                    'title': work_type['title'],
                    'abbr': work_type['abbr']
                }
            ))

            if work_type['id'] in work_types_id:
                results[work_type['id']] = WorkType(
                    title=work_type['title'],
                    abbr=work_type['abbr']
                )

        # Запись в кэш для последующих запросов
        await cache_repository.put_caches(session.session_id, child.child_id, new_caches)

        return results

    @classmethod
    async def _get_persons_name(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            persons_id: set[int]
    ) -> dict[int, str]:
        """
        Получение имен одноклассников

        :param cache_repository: CacheRepository для получения имен из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются имена одноклассников
        :param persons_id: идентификаторы одноклассников
        :return: имена одноклассников по идентификаторам
        """

        if not persons_id:
            return {}

        # Получение имен одноклассников из кэша
        persons_id_key = [f"person|{person_id}" for person_id in persons_id]
        caches = await cache_repository.get_caches(session.session_id, child.child_id, persons_id_key)
        results = {
            int(cache.key.split("|")[1]): cache.value['name']
            for cache in caches
        }

        # Если из кэша все необходимые имена одноклассников получены
        if persons_id == results.keys():
            return results

        # Иначе запрос к Дневнику.ру
        persons = await dnr.get_group_persons(child.group_id)

        new_caches = []

        for person in persons:
            new_caches.append((
                f"person|{person['id']}",
                {
                    'name': person['shortName']
                }
            ))

            if person['id'] in persons_id:
                results[person['id']] = person['shortName']

        # Запись в кэш для последующих запросов
        await cache_repository.put_caches(session.session_id, child.child_id, new_caches)

        return results

    @classmethod
    async def _get_extracurricular_activities(
            cls, extracurricular_activity_repository: ExtracurricularActivityRepository,
            child: Child,
            period: tuple[datetime, datetime],
    ) -> dict[date, list[ScheduleExtracurricularActivity]]:
        """
        Получение внеурочных занятий за период

        :param extracurricular_activity_repository: ExtracurricularActivityRepository для получения внеурочных занятий
        :param child: ребенок (профиль), для которого требуются внеурочные занятия
        :param period: период в расписании
        :return: внеурочные занятия по дням
        """

        # Внеурочные занятия учебной группы (класса) за период
        extracurricular_activities = await extracurricular_activity_repository.get_extracurricular_activities(
            child.school_id, child.group_id, period)

        results = {}
        for extracurricular_activity in extracurricular_activities:
            start_time = astimezone(extracurricular_activity.start_time, child.timezone)
            start_date = start_time.date()

            if results.get(start_date) is None:
                results[start_date] = []

            start = time.fromisoformat(extracurricular_activity.hours['start'])
            end = time.fromisoformat(extracurricular_activity.hours['end'])
            hours_string = extracurricular_activity.hours['string']

            results[start_date].append(ScheduleExtracurricularActivity(
                subject=extracurricular_activity.subject,
                place=str(extracurricular_activity.place),
                hours=ScheduleHours(
                    start=start_time.replace(hour=start.hour, minute=start.minute),
                    end=start_time.replace(hour=end.hour, minute=end.minute),
                    string=hours_string
                )
            ))

        return results

    @classmethod
    def _calc_avg(cls, marks: list[MarkLog], others_marks: list[MarksOther], avg = False) -> Optional[MarkLog]:
        """
        Подсчет среднего балла оценок

        :param marks: оценки пользователя
        :param others_marks: оценки одноклассников
        :param avg: подсчитать среднее арифметическое, иначе считается медиана
        :return: средняя оценка, если оценки есть и они успешно обработаны
        """

        # "Настроения" оценок берутся из самих оценок
        moods: dict[int, Literal["good", "average", "bad", "more"]] = {}
        all_marks = []

        for mark in marks:
            if (value := mark.value.replace('+', '').replace('-', '')).isnumeric():
                int_value = int(value)
                moods[int_value] = mark.mood
                all_marks.append(int_value)

        for other_marks in others_marks:
            for mark in other_marks.marks:
                if (value := mark.value.replace('+', '').replace('-', '')).isnumeric():
                    int_value = int(value)
                    moods[int_value] = mark.mood
                    all_marks.append(int_value)

        if len(all_marks) != 0:
            avg_value = round_or_int((mean if avg else median)(all_marks))  # Подсчет необходимого среднего и округление

            # Если в доступных moods нет нужного настроения, то берется из mark5_moods
            avg = MarkLog(
                value=str(avg_value).replace('.', ','),
                mood=moods.get(int(avg_value), mark5_moods.get(int(avg_value), MarkLog.default_mood())),
                work=None,
                created=None
            )
        else:
            avg = None

        return avg

    @classmethod
    def _get_lesson_url(cls, school_id: int, lesson_id: int) -> str:
        """
        Сборка ссылки на урок в Дневнике.ру

        :param school_id: идентификаторы образовательной организации
        :param lesson_id: идентификатор урока
        :return: ссылка на урок в Дневнике.ру
        """

        url = URL.build(
            scheme='https',
            host='schools.dnevnik.ru',
            path='/lesson',
            query={
                'school': school_id,
                'lesson': lesson_id
            }
        )

        return str(url)

    @classmethod
    async def _get_schedule_posts(
            cls, school_post_repository: SchoolPostRepository,
            school_post_like_repository: SchoolPostLikeRepository, school_post_vision_repository: SchoolPostVisionRepository,
            child: Child, session: Session,
            period: tuple[date, date]
    ) -> tuple[dict[date, list[SchoolPost]], list[int], list[int]]:
        """
        Получение постов с мероприятиями для расписания и наличия реакций и отметок "увидел" на постах

        :param school_post_repository: SchoolPostRepository для получения постов
        :param school_post_like_repository: SchoolPostLikeRepository для получения реакций на пост
        :param school_post_vision_repository: SchoolPostVisionRepository для получения отметок "увидел" у постов
        :param child: ребенок (профиль), для которого требуются посты
        :param session: сессия пользователя
        :param period: период расписания
        :return: посты по дням, какие посты с реакциями пользователя, какие посты пользователь увидел
        """

        start_date, end_date = period

        # Получение постов с мероприятиями в данном периоде
        posts = await school_post_repository.get_schedule_posts(child.school_id, start_date, end_date)
        post_ids = [post.post_id for post in posts]

        # Получение реакций и отметок "увидел" для этих постов

        likes = await school_post_like_repository.has_my_likes(session.parent_id, post_ids)
        my_likes = [like.post_id for like in likes]

        visions = await school_post_vision_repository.has_my_visions(session.parent_id, post_ids)
        my_visions = [vision.post_id for vision in visions]

        posts_by_date: dict[date, list[SchoolPost]] = {}
        for post in posts:
            if post.schedule_date not in posts_by_date:
                posts_by_date[post.schedule_date] = []
            posts_by_date[post.schedule_date].append(post)

        return posts_by_date, my_likes, my_visions

    async def getLessonRatingStats(self, session_id: str, rating_key: str) -> LessonRatingStatsApiResponse:
        async with self.uow_factory() as uow:
            try:
                params = rating_key.split('.')

                period_id = unzip_int(params[0])
                subject_id = unzip_int(params[1])

                lesson_date = datetime.fromisoformat(params[2]).date()
            except (ValueError, IndexError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='getLessonRatingStats',
                    session_id=session_id,
                    status=False,
                    value=f"rating_key: {rating_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return LessonRatingStatsApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                old, new = await self._get_change_avg(dnr, child, period_id, lesson_date, subject_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getLessonRatingStats)

            return LessonRatingStatsApiResponse(
                answer=LessonRatingStatsResult(
                    oldAvgMark=old,
                    newAvgMark=new
                )
            )

    @classmethod
    async def _get_change_avg(
            cls, dnr: AioDnevnikruApi,
            child: Child,
            period_id: int, lesson_date: date, subject_id: int
    ) -> tuple[MarkLog, MarkLog]:
        """
        Подсчет изменения среднего балла по предмету за день

        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param child: ребенок (профиль), дял которого необходимо изменение среднего балла
        :param period_id: идентификатор отчетного периода
        :param lesson_date: отчетный день для сравнения
        :param subject_id: идентификатор учебного предмета
        :return: средний балл за день до отчетного дня и на конец дня
        """

        # Средние баллы учебной группы (класса) на 2 дня
        before, after = await gather(
            dnr.get_group_avg_marks_by_date(child.group_id, period_id, lesson_date - timedelta(days=1)),
            dnr.get_group_avg_marks_by_date(child.group_id, period_id, lesson_date)
        )

        old_avg: Optional[str] = None
        new_avg: Optional[str] = None

        # Поиск необходимых оценок пользователя

        for person in before:
            if person['person'] != child.child_id:
                continue

            for subject in person['per-subject-averages']:
                if subject['subject'] != subject_id:
                    continue

                old_avg = subject['avg-mark-value']
                break
            if old_avg:
                break

        for person in after:
            if person['person'] != child.child_id:
                continue

            for subject in person['per-subject-averages']:
                if subject['subject'] != subject_id:
                    continue

                new_avg = subject['avg-mark-value']
                break
            if new_avg:
                break

        # Используется mark5
        old = MarkLog(
            mood=mark5_moods.get(int(float(old_avg.replace(',', '.'))), MarkLog.default_mood()),
            value=old_avg,
            work=None,
            created=None
        ) if old_avg else None
        new = MarkLog(
            mood=mark5_moods.get(int(float(new_avg.replace(',', '.'))), MarkLog.default_mood()),
            value=new_avg,
            work=None,
            created=None
        ) if new_avg else None

        return old, new


    @classmethod
    async def _get_periods(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child
    ) -> list[dict]:
        """
        Получение отчетных периодов в текущем году

        :param cache_repository: CacheRepository для получения отчетных периодов из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются отчетные периоды
        :return: список отчетных периодов
        """

        cache_key = "periods"

        # Получение из кэша
        if cache := await cache_repository.get_cache(session.session_id, child.child_id, cache_key):
            return cache.value
        else:
            # Запрос из Дневника.ру
            periods = await dnr.get_reporting_periods(child.group_id)

            # Сохранение в кэш для последующих запросов
            await cache_repository.put_cache(session.session_id, child.child_id, cache_key, periods)

            return periods

    @classmethod
    async def _get_period(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            day: date
    ) -> dict:
        """
        Получение отчетного периода, в который входит день

        :param cache_repository: CacheRepository для получения отчетных периодов из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуется отчетный период
        :param day: дата дня
        :return: отчетный период
        """

        periods = await cls._get_periods(cache_repository, dnr, session, child)
        periods = sorted(periods, key=lambda p: datetime.fromisoformat(p['start']))

        return cls._get_active_period(periods, day)

    @classmethod
    def _get_active_period(cls, periods: list[dict], day: date) -> dict:
        """
        Получение отчетного периода, в который входит день

        :param periods: отчетные периоды, отсортированные по возрастанию
        :param day: дата дня
        :return: отчетный период
        """

        active_period = None
        for number, period in enumerate(periods):
            start = datetime.fromisoformat(period['start']).date()

            # Если следующий отчетный период уже после дня, то день входит в прошлый
            if start > day:
                active_period = periods[max(0, number - 1)]  # Если день до первого отчетного периода, то первый
                break

        # Если нет такого отчетного периода, который начинается после дня, то это последний отчетный период
        if active_period is None:
            active_period = periods[-1]

        return active_period

    async def getMarks(self, session_id: str, last: int) -> MarksApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            now = datetime_now(child.timezone)
            from_date = (now - timedelta(days=last)).date()

            try:
                recent_marks, (period_marks, active_period_id) = await gather(
                    self._get_recent_marks(uow.cache_repository, dnr, session, child, from_date, limit=50),
                    self._get_period_marks(uow.cache_repository, dnr, session, child)
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getMarks)

            return MarksApiResponse(
                answer=MarksResult(
                    recentMarks=recent_marks,
                    periodMarks=period_marks,
                    ratingKey=zip_int(active_period_id)
                )
            )

    @classmethod
    async def _get_recent_marks(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            from_date: date, limit: int
    ) -> list[MarkLast]:
        """
        Получение последних по дате выставления оценок

        :param cache_repository: CacheRepository для получения типов работ и отчетных периодов из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются последние оценки
        :param from_date: начиная это даты будут получены оценки
        :param limit: лимит оценок по каждому предмету отдельно
        :return: список последних оценок
        """

        recent_marks = await dnr.get_person_recent_marks(child.child_id, child.group_id, from_date, limit=limit)

        if not recent_marks:
            return []

        works = {work['id']: work for work in recent_marks['works']}
        subjects = {subject['id']: subject['name'] for subject in recent_marks['subjects']}

        periods: dict[int, dict] = {}

        work_types_id: set[int] = {mark['workType'] for mark in recent_marks['marks']}
        period_works: set[int] = {mark['work'] for mark in recent_marks['marks'] if mark['lesson'] is None}

        # Если есть оценки за экзамен или отчетный период
        if period_works:
            work_types, _periods = await gather(
                cls._get_work_types(cache_repository, dnr, session, child, work_types_id),
                cls._get_periods(cache_repository, dnr, session, child)
            )
            periods = {_period['number']: _period for _period in _periods}
        else:
            work_types = await cls._get_work_types(cache_repository, dnr, session, child, work_types_id)

        marks: list[MarkLast] = []

        for mark in recent_marks['marks']:
            work = works[mark['work']]
            subject = subjects.get(work['subjectId'], "Неизвестный предмет")
            work_type = work_types.get(mark['workType'])

            period: Optional[str] = None

            # Оценка за экзамен или отчетный период
            if mark['lesson'] is None:
                if work['type'] == "PeriodMark":  # Оценка за год или отчетный период
                    if work['periodType'] == 'Year':  # Годовая
                        period = "Годовая"
                    else:  # За отчетный период
                        period = periods[work['periodNumber']]['name']
                elif work['type'] == "Exam":  # Итоговый экзамен
                    period = "Экзамен"
                elif work['type'] == "PeriodFinalMark":  # Итоговая (после экзамена и годовой)
                    period = "Итоговая"

                if period:
                    work_type = WorkType(title=period, abbr=period)

            lesson_date = datetime.fromisoformat(work['targetDate']).date()  # Дата урока
            human_lesson_date = None if period else lesson_date.strftime('%e %b.').strip()  # Например '9 дек.'

            marks.append(MarkLast(
                mark=MarkLog(
                    value=mark['textValue'],
                    mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                    work=work_type,
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                ),
                subject=subject,
                lessonDate=lesson_date,
                humanLessonDate=human_lesson_date,
                ratingKey=f"w{zip_int(mark['work'])}" if mark['lesson'] is None else f"l{zip_int(mark['lesson'])}"
            ))

        return marks

    @classmethod
    async def _get_period_marks(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child
    ) -> tuple[list[MarksSubjectPeriod], int]:
        """
        Получение оценок по предметам за текущий отчетный период

        :param cache_repository: CacheRepository для получения отчетных периодов из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются оценки
        :return: все оценки по предметам и идентификатор текущего отчетного периода
        """

        now = datetime_now(child.timezone).date()
        active_period = await cls._get_period(cache_repository, dnr, session, child, now)

        start = datetime.fromisoformat(active_period['start']).date()
        finish = datetime.fromisoformat(active_period['finish']).date()

        # Оценки за отчетный период, средние баллы и оценки за отчетный период
        _marks, _avg_marks, final_marks = await gather(
            dnr.get_person_marks(child.child_id, child.group_id, start, finish),
            dnr.get_group_avg_marks(child.group_id, start, finish),
            dnr.get_person_final_marks(child.child_id, child.group_id)
        )

        avg_marks: dict[int, dict] = {}  # Средние баллы ребенка (профиля)
        for person in _avg_marks:
            if person['person'] != child.child_id:
                continue

            for mark in person['per-subject-averages']:
                avg_marks[mark['subject']] = mark

        work_types_id = {mark['workType'] for mark in _marks}
        work_types_id.update({work['workType'] for work in final_marks['works']})

        _lessons, work_types = await gather(
            dnr.get_many_lessons([mark['lesson'] for mark in _marks]),
            cls._get_work_types(cache_repository, dnr, session, child, work_types_id)
        )

        lessons = {lesson['id']: lesson for lesson in _lessons}

        # Все оценки по предметам за отчетный период
        marks: dict[int, list[dict]] = {}
        for mark in _marks:
            subject_id = lessons[mark['lesson']]['subject']['id']
            if marks.get(subject_id) is None:
                marks[subject_id] = []
            marks[subject_id].append(mark)

        subjects = {subject['id']: subject['name'] for subject in final_marks['subjects']}
        works = {work['id']: work for work in final_marks['works'] if work['periodNumber'] == active_period['number']}
        period_marks = {work['subjectId']: mark for mark in final_marks['marks'] if (work := works.get(mark['work']))}

        result = []  # Предметы с оценками
        result_without_marks = []  # Предметы без оценок

        for subject_id, subject in sorted(subjects.items(), key=lambda subject: subject[1]):  # Сортировка по алфавиту
            if not marks.get(subject_id):
                result_without_marks.append(MarksSubjectPeriod(
                    subject=subject,
                    marks=[],
                    averageMark=None,
                    periodMark=None,
                    ratingKey=f"{zip_int(subject_id)}.{zip_int(active_period['id'])}"
                ))
                continue

            result.append(MarksSubjectPeriod(
                subject=subject,
                marks=[MarkLog(
                    mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                    value=mark['textValue'],
                    work=work_types.get(mark['workType']),
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone),
                    ratingKey=f"w{zip_int(mark['work'])}" if mark['lesson'] is None else f"l{zip_int(mark['lesson'])}"
                ) for mark in marks[subject_id]],
                averageMark=MarkLog(
                    value=value,
                    mood=mark5_moods.get(round(float(value.replace(',', '.'))), MarkLog.default_mood()),
                    work=None,
                    created=None
                ) if (value := avg_marks.get(subject_id, {}).get('avg-mark-value')) else None,
                periodMark=MarkLog(
                    mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                    value=mark['textValue'],
                    work=work_types.get(mark['workType']),
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                ) if (mark := period_marks.get(subject_id)) else None,
                ratingKey=f"{zip_int(subject_id)}.{zip_int(active_period['id'])}"
            ))

        result.extend(result_without_marks)  # Предметы без оценок всегда после предметов с оценками

        return result, active_period['id']

    async def getMarksRatingStats(self, session_id: str, rating_key: str, api: int = None) -> Union[MarksRatingStatsApiResponse0x1B, MarksRatingStatsApiResponse]:
        if api == 0:
            answer_type = MarksRatingStatsApiResponse0x1B
            result_type = MarksRatingStatsResult0x1A
        else:
            answer_type = MarksRatingStatsApiResponse
            result_type = MarksRatingStatsResult

        async with self.uow_factory() as uow:
            try:
                key_type = rating_key[0]

                entity_id = unzip_int(rating_key[1:])
            except (ValueError, IndexError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='getMarksRatingStats',
                    session_id=session_id,
                    status=False,
                    value=f"rating_key: {rating_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            # Выделенные одноклассники в рейтинге
            _highlighting_persons = await uow.highlighting_person_repository.get_highlighting_persons(parent.parent_id)
            highlighting_persons = {person.person_id for person in _highlighting_persons}

            # Рейтинг по оценке за работу (без привязки к уроку)
            if key_type == 'w':
                try:
                    _marks = await dnr.get_marks_by_work(entity_id)
                except BaseDnevnikruException as e:
                    if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                        raise SessionError(session_id=session.session_id) from e
                    raise

                persons_id: set[int] = {mark['person'] for mark in _marks}
                persons = await self._get_persons_name(uow.cache_repository, dnr, session, child, persons_id)

                marks = []
                others_marks = []
                for mark in _marks:
                    mark_log = MarkLog(
                        value=mark['textValue'],
                        mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                        work=None,
                        created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                    )

                    if mark['person'] == child.child_id:
                        marks.append(mark_log)
                    elif name := persons.get(mark['person']):
                        others_marks.append(MarksOther(
                            name=name,
                            personKey=zip_int(mark['person']),
                            isHighlighting=mark['person'] in highlighting_persons,
                            marks=[mark_log]
                        ))

                avg = self._calc_avg(marks, others_marks, avg=True)  # Средний балл оценок

                # Сортировка одноклассников по оценке и наличию выделения
                others_marks = sorted(
                    others_marks,
                    key=self._key_others_marks,
                    reverse=True
                )

                await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getMarksRatingStats)

                return answer_type(
                    answer=result_type(
                        othersMarks=others_marks,
                        avgGroupMark=avg,
                        oldAvgMark=None,
                        newAvgMark=None,
                        hasAbilityPraise=parent.parent_id != child.child_id
                    )
                )

            # Рейтинг по оценке за урок
            try:
                lesson, periods = await gather(
                    dnr.get_lesson(entity_id),
                    self._get_periods(uow.cache_repository, dnr, session, child)
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            lesson_date = datetime.fromisoformat(lesson['date']).date()
            period_id = self._get_active_period(periods, lesson_date)['id']
            subject_id = lesson['subject']['id']

            async def get_marks_and_persons():
                __marks = await dnr.get_marks_by_lesson(entity_id)
                __persons_id: set[int] = {__mark['person'] for __mark in __marks}
                __persons = await self._get_persons_name(uow.cache_repository, dnr, session, child, __persons_id)
                return __marks, __persons

            (old, new), (_marks, persons) = await gather(
                self._get_change_avg(dnr, child, period_id, lesson_date, subject_id),
                get_marks_and_persons()
            )

            marks = []
            others_marks = {}
            for mark in _marks:
                mark_log = MarkLog(
                    value=mark['textValue'],
                    mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                    work=None,
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                )

                if mark['person'] == child.child_id:
                    marks.append(mark_log)
                elif name := persons.get(mark['person']):
                    if (other := others_marks.get(mark['person'])) is None:
                        other = MarksOther(
                            name=name,
                            personKey=zip_int(mark['person']),
                            isHighlighting=mark['person'] in highlighting_persons,
                            marks=[]
                        )
                        others_marks[mark['person']] = other
                    other.marks.append(mark_log)

            # Сортировка одноклассников по оценке и наличию выделения
            others_marks = sorted(
                others_marks.values(),
                key=self._key_others_marks,
                reverse=True
            )

            avg = self._calc_avg(marks, others_marks)  # Средний балл оценок

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getMarksRatingStats)

            return answer_type(
                answer=result_type(
                    othersMarks=others_marks,
                    avgGroupMark=avg,
                    oldAvgMark=old,
                    newAvgMark=new,
                    hasAbilityPraise=parent.parent_id != child.child_id
                )
            )

    async def getMarksSubjectRating(self, session_id: str, rating_key: str) -> MarksSubjectRatingApiResponse:
        async with self.uow_factory() as uow:
            try:
                key = re.fullmatch(r'(?:(?P<subject_id>[0-9a-z]{1,13})\.)?(?P<period_id>[0-9a-z]{1,13})', rating_key)
                assert key is not None, "rating_key format is invalid"

                subject_id = unzip_int(key.group('subject_id')) if key.group('subject_id') else None

                period_id = unzip_int(key.group('period_id'))
            except (ValueError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='getMarksSubjectRating',
                    session_id=session_id,
                    status=False,
                    value=f"rating_key: {rating_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return MarksSubjectRatingApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            periods = await self._get_periods(uow.cache_repository, dnr, session, child)

            try:
                period = next(filter(lambda p: p['id'] == period_id, periods))
            except StopIteration as e:
                await uow.log_repository.add_log(
                    path='getMarksSubjectRating',
                    session_id=session_id,
                    status=False,
                    value=f"rating_key: {rating_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return MarksSubjectRatingApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            start = datetime.fromisoformat(period['start']).date()
            finish = datetime.fromisoformat(period['finish']).date()

            try:
                avg_marks = await dnr.get_group_avg_marks(child.group_id, start, finish)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            persons_id: set[int] = {person['person'] for person in avg_marks}
            persons_name = await self._get_persons_name(uow.cache_repository, dnr, session, child, persons_id)

            _highlighting_person = await uow.highlighting_person_repository.get_highlighting_persons(parent.parent_id)
            highlighting_person = {person.person_id for person in _highlighting_person}

            class_rating: list[tuple[MarksOther, float, int]] = []

            # Общий рейтинг в классе по всем предметам
            if subject_id is None:
                for person in avg_marks:
                    if len(person['per-subject-averages']) == 0 or not (name := persons_name.get(person['person'])):
                        continue

                    # Средний балл всех средних баллов
                    sum_marks = sum(float(mark['avg-mark-value'].replace(',', '.')) for mark in person['per-subject-averages'])
                    avg_mark = round_or_int(sum_marks / len(person['per-subject-averages']))

                    class_rating.append(
                        (
                            MarksOther(
                                name=name,
                                personKey=None if person['person'] == child.child_id else zip_int(person['person']),
                                isHighlighting=None if person['person'] == child.child_id else person['person'] in highlighting_person,
                                marks=[MarkLog(
                                    mood=mark5_moods.get(int(avg_mark), MarkLog.default_mood()),
                                    value=str(avg_mark).replace('.', ','),
                                    work=None,
                                    created=None
                                )]
                            ),
                            avg_mark,
                            person['person']
                        )
                    )

            else:
                for person in avg_marks:
                    if not (name := persons_name.get(person['person'])):
                        continue

                    for subject in person['per-subject-averages']:
                        if subject['subject'] != subject_id:
                            continue

                        avg_mark = float(subject['avg-mark-value'].replace(',', '.'))

                        class_rating.append(
                            (
                                MarksOther(
                                    name=name,
                                    personKey=None if person['person'] == child.child_id else zip_int(person['person']),
                                    isHighlighting=None if person['person'] == child.child_id else person['person'] in highlighting_person,
                                    marks=[MarkLog(
                                        mood=mark5_moods.get(round(avg_mark), MarkLog.default_mood()),
                                        value=subject['avg-mark-value'],
                                        work=None,
                                        created=None
                                    )]
                                ),
                                avg_mark,
                                person['person']
                            )
                        )

            # Сортировка по среднему баллу. Если средний балл одинаковый, то сам ребенок (профиль) будет выше
            rating = sorted(class_rating, key=lambda r: (r[1], r[2] == child.child_id), reverse=True)

            # Места с одинаковым средним баллом имеют одинаковый номер места
            last_number = 0
            last_avg = None
            for i, (other_mark, avg_mark, _) in enumerate(rating):
                if avg_mark == last_avg:
                    other_mark.number = last_number
                else:
                    other_mark.number = i
                    last_number = i
                last_avg = avg_mark

            # Место в рейтинге ребенка (профиля)
            me: Optional[int] = None
            for i, (_, _, person_id) in enumerate(rating):
                if person_id == child.child_id:
                    me = i

            # Прошлое место в рейтинге
            old_mark: Optional[MarksOther] = None
            old = await uow.rating_repository.get_rating(child.child_id, period_id, subject_id or -1)

            if old is not None:
                old_mark = MarksOther(
                    number=old.number,
                    name=persons_name.get(child.child_id, "Я"),
                    personKey=None,
                    isHighlighting=None,
                    marks=[MarkLog(
                        mood=old.mood,
                        value=old.avg,
                        work=None,
                        created=None
                    )]
                )

                # Если прошлое место в рейтинге и средний балл не изменился
                if me is not None and old_mark == rating[me][0]:
                    old_mark = None


            # Обновление прошлого места в рейтинге
            if me is not None:
                await uow.rating_repository.put_rating(
                    child.child_id,
                    period_id,
                    subject_id or -1,
                    rating[me][0].number,
                    rating[me][0].marks[0].value,
                    rating[me][0].marks[0].mood
                )
            else:
                await uow.rating_repository.delete_rating(child.child_id, period_id, subject_id or -1)

            # Учет в сортировке выделение одноклассников (в самый последний момент)
            rating = sorted(rating, key=lambda r: r[0].isHighlighting is True, reverse=True)

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getMarksSubjectRating)

            return MarksSubjectRatingApiResponse(
                answer=MarksSubjectRatingResult(
                    rating=[other_mark for (other_mark, _, _) in rating],
                    oldMark=old_mark
                )
            )

    async def getFinalMarks(self, session_id: str) -> MarksFinalApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                marks, periods = await gather(
                    dnr.get_person_final_marks(child.child_id, child.group_id),
                    self._get_periods(uow.cache_repository, dnr, session, child)
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            works = {work['id']: work for work in marks['works']}
            work_types_id = {work['workType'] for work in marks['works']}
            subjects = {subject['id']: subject['name'] for subject in marks['subjects']}

            work_types = await self._get_work_types(uow.cache_repository, dnr, session, child, work_types_id)

            final_marks: dict[int, dict[int, MarkLog]] = {}

            for mark in marks['marks']:
                work = works.get(mark['work'])

                if work is None:
                    continue
                if final_marks.get(work['subjectId']) is None:
                    final_marks[work['subjectId']] = {}

                period_number = -1 if work['periodType'] == 'Year' else work['periodNumber']

                final_marks[work['subjectId']][period_number] = MarkLog(
                    mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                    value=mark['textValue'],
                    work=work_types.get(work['workType']),
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone),
                    ratingKey=f"w{zip_int(mark['work'])}"
                )

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getFinalMarks)

            return MarksFinalApiResponse(
                answer=MarksFinalResult(
                    countPeriods=len(periods),
                    finalMarks=[MarksSubjectFinal(
                        subject=subjects.get(subject_id, "Неизвестный предмет"),
                        marks=[period_marks.get(i) for i in range(len(periods))],
                        finalMark=period_marks.get(-1)
                    ) for subject_id, period_marks in final_marks.items()]
                )
            )
