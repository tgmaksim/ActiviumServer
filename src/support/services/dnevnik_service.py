import re

from asyncio import gather
from typing import Callable, Optional, Literal

from httpx import AsyncClient
from datetime import datetime, timedelta, time, date, UTC

from yarl import URL

from dnevnikru.exceptions import BaseDnevnikruException
from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi

from ...dependencies.zip_int import zip_int
from ...dependencies.auth import check_session
from ...dependencies.httpx import get_httpx_client
from ...dependencies.datetime import datetime_now, astimezone

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
    MarksApiResponse,
    MarksFinalResult,
    MarksSubjectFinal,
    MarksSubjectPeriod,
    ScheduleApiResponse,
    MarksFinalApiResponse,
    MarksRatingStatsResult,
    LessonRatingStatsResult,
    ScheduleHomeworkDocument,
    MarksSubjectRatingResult,
    MarksRatingStatsApiResponse,
    LessonRatingStatsApiResponse,
    MarksSubjectRatingApiResponse,
    ScheduleExtracurricularActivity,
)


__all__ = ['DnevnikService']

mark_moods: dict[int, Literal["good", "average", "bad"]] = \
    {5: "good", 4: "good", 3: "average", 2: "bad", 1: "bad"}
round_or_int = lambda n: int(n) if (r := round(n, 2)) == int(n) else r


class DnevnikService(BaseService[AppUnitOfWork]):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def getSchedule(self, session_id: str, before: int, after: int) -> ScheduleApiResponse:
        async with self.uow_factory() as uow:
            if after + before > 30:
                await uow.log_repository.add_log(path='getSchedule', session_id=session_id, status=False,
                                                 value=f"IntervalTooLong: {after} + {before} = {after + before}")
                return ScheduleApiResponse(
                    status=False,
                    error=ApiError(
                        type="IntervalTooLong",
                        errorMessage=f"Максимальный размер интервала равен 30 дням ({after + before} дней запрошено)"
                    )
                )

            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = parent.active_child

            dnr = AioDnevnikruApi(get_httpx_client(), session.dnevnik_token)
            now = datetime_now(child.timezone)
            start = (now - timedelta(days=before)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = start.date()
            end = (now + timedelta(days=after)).replace(hour=23, minute=59, second=59, microsecond=99999)
            end_date = end.date()

            person_schedule: dict  # расписание конкретно для обучающегося
            files: dict[int, list[ScheduleHomeworkDocument]]  # файлы к домашнему заданию по идентификаторам уроков
            marks: dict[int, list[MarkLog]]  # оценки по урокам
            others_marks: dict[int, list[MarksOther]]  # оценки класса по урокам и обучающимся

            try:
                (person_schedule, files), (marks, others_marks), active_period = await gather(
                    self._get_person_schedule(dnr, child, start_date, end_date),
                    self._get_schedule_marks(uow.cache_repository, dnr, uow.highlighting_person_repository, session, child, start_date, end_date),
                    self._get_period(uow.cache_repository, dnr, session, child, now.date())
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            lessons_id = []
            for day in person_schedule['days']:
                for lesson in day['lessons']:
                    lessons_id.append(lesson['id'])

            # Показывать только открытые заметки для родителя
            only_public_notes = parent.parent_id != parent.active_child_id
            notes = await uow.lesson_note_repository.get_notes(parent.active_child_id, lessons_id, only_public=only_public_notes)

            ea = await self._get_extracurricular_activities(uow.extracurricular_activity_repository, child, (start, end))

            result = []
            for day in person_schedule['days']:
                subjects = {subject['id']: subject['name'] for subject in day['subjects']}
                works = {work['id']: work for work in day['works']}
                work_types = {work_type['id']: work_type for work_type in day['workTypes']}
                homeworks: dict[int, list[str]] = {}
                for homework in day['homeworks']:
                    if homeworks.get(homework['lesson']) is None:
                        homeworks[homework['lesson']] = []
                    homeworks[homework['lesson']].append(homework['text'])
                logs = {lesson_log['lesson']: [MarkLog(
                    mood=MarkLog.default_mood(),
                    value=value,
                    work=None,
                    created=astimezone(datetime.fromisoformat(lesson_log['createdDate']).replace(tzinfo=UTC), child.timezone)
                )] for lesson_log in day['lessonLogEntries'] if (value := MarkLog.log_value(lesson_log['status']))}

                day_date = datetime.fromisoformat(day['date'])

                hours = await uow.hour_repository.get_hours(child.school_id, day_date.month, day_date.weekday())

                lessons = []
                for lesson in sorted(day['lessons'], key=lambda l: l['number']):
                    lesson_works = [WorkType(
                        title=work_type['name'],
                        abbr=work_type['abbreviation']
                    ) for work_id in lesson['works'] if (work_type := work_types.get(works.get(work_id, {}).get('workType')))
                                                        and work_type['kind'] != 'DefaultNewLessonWork']

                    if hours:
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

                    avg = self._calc_avg(marks.get(lesson['id'], []), others_marks.get(lesson['id'], []))

                    lessons.append(ScheduleLesson(
                        lessonKey=zip_int(lesson['id']),
                        number=lesson['number'] - 1,  # Начало с 0
                        subject=subjects.get(lesson['subjectId'], "Неизвестный предмет"),
                        place=lesson['place'],
                        works=lesson_works,
                        hours=lesson_hours,
                        logs=marks.get(lesson['id'], []) + logs.get(lesson['id'], []),
                        othersMarks=others_marks.get(lesson['id'], []),
                        avgGroupLessonMark=avg,
                        homework='; '.join(homeworks.get(lesson['id'], [])) or None,
                        note=note.text if (note := notes.get(lesson['id'])) else None,
                        files=files.get(lesson['id'], []),
                        ratingKey=f"{zip_int(active_period['id'])}.{zip_int(lesson['subjectId'])}.{day_date.date()}",
                        dnevnikruUrl=self._get_lesson_url(child.school_id, lesson['id'])
                    ))

                result.append(ScheduleDay(
                    date=day_date.date(),
                    lessons=lessons,
                    ea=ea.get(day_date.date(), []),
                ))

            await uow.statistic_repository.add_statistic(parent.parent_id, 'getSchedule')

            return ScheduleApiResponse(
                answer=ScheduleResult(
                    schedule=result,
                    timezone=child.timezone,
                    hasAbilityPraise=parent.parent_id != parent.active_child_id
                )
            )

    @classmethod
    async def _get_person_schedule(
            cls, dnr: AioDnevnikruApi,
            child: Child,
            start_date: date, end_date: date
    ) -> tuple[dict, dict[int, list[ScheduleHomeworkDocument]]]:
        schedule = await dnr.get_person_schedule(child.child_id, child.group_id, start_date, end_date)

        lessons_id = []
        homeworks_id = []
        for day in schedule['days']:
            for homework in day['homeworks']:
                lessons_id.append(homework['lesson'])
                homeworks_id.append(homework['id'])

        homeworks = await cls._get_homeworks_files(dnr, homeworks_id=homeworks_id)

        return schedule, {lessons_id[i]: files for i in range(len(homeworks_id)) if (files := homeworks.get(homeworks_id[i])) is not None}

    @classmethod
    async def _get_homeworks_files(
            cls, dnr: AioDnevnikruApi,
            homeworks_id: list[int]
    ) -> dict[int, list[ScheduleHomeworkDocument]]:
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
        my_marks = {}
        others_marks = {}

        marks = await dnr.get_group_marks(child.group_id, start_date, end_date)

        work_types_id = set()
        persons_id = set()
        for mark in marks:
            work_types_id.add(mark['workType'])
            persons_id.add(mark['person'])

        work_types, persons, _highlighting_persons = await gather(
            cls._get_work_types(cache_repository, dnr, session, child, work_types_id),
            cls._get_persons_name(cache_repository, dnr, session, child, persons_id),
            highlighting_person_repository.get_highlighting_persons(session.parent_id)
        )

        highlighting_persons = {person.person_id for person in _highlighting_persons}

        for mark in marks:
            mood = mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood()

            if mark['person'] == child.child_id:
                if my_marks.get(mark['lesson']) is None:
                    my_marks[mark['lesson']] = []

                my_marks[mark['lesson']].append(MarkLog(
                    mood=mood,
                    value=mark['textValue'],
                    work=work_types.get(mark['workType']),
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                ))
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

        return my_marks, {lesson_id: sorted(
            others_marks[lesson_id].values(),
            key=cls._key_others_marks,
            reverse=True
        ) for lesson_id in others_marks}

    @classmethod
    def _key_others_marks(cls, other_marks: MarksOther):
        marks = []
        for _mark in other_marks.marks:
            mark = _mark.value.replace(',', '.')
            pm = 0
            if '+' in mark:
                mark = mark.replace('+', '')
                pm = +0.25
            elif '-' in mark:
                mark = mark.replace('-', '')
                pm = -0.25

            if mark.isnumeric():
                marks.append(float(mark) + pm)

        if len(marks) == 0:
            return 0, []
        return other_marks.isHighlighting, sum(marks) / len(marks), marks

    @classmethod
    async def _get_work_types(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            work_types_id: set[int]
    ):
        if not work_types_id:
            return {}

        now = datetime_now()
        cache_key_factory = lambda w: f"workType|{w}"

        caches = await cache_repository.get_caches(session.session_id, list(map(cache_key_factory, work_types_id)))
        results = {int(cache.key.split("|")[1]): WorkType(
            title=cache.value['title'],
            abbr=cache.value['abbr']
        ) for cache in caches if now - cache.updated_at < timedelta(days=28)}

        if len(results) == len(work_types_id):
            return results

        work_types = await dnr.get_work_types(child.school_id)

        new_caches = []

        for work_type in work_types:
            new_caches.append((
                cache_key_factory(work_type['id']),
                {'title': work_type['title'], 'abbr': work_type['abbr']}
            ))

            if work_type['id'] in work_types_id:
                results[work_type['id']] = WorkType(
                    title=work_type['title'],
                    abbr=work_type['abbr']
                )

        await cache_repository.put_caches(session.session_id, new_caches)

        return results

    @classmethod
    async def _get_persons_name(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            persons_id: set[int]
    ) -> dict[int, str]:
        if not persons_id:
            return {}

        now = datetime_now()
        cache_key_factory = lambda p: f"person|{p}"

        caches = await cache_repository.get_caches(session.session_id, list(map(cache_key_factory, persons_id)))
        results = {int(cache.key.split("|")[1]): cache.value['name'] for cache in caches
                   if now - cache.updated_at < timedelta(days=28)}

        if len(results) == len(persons_id):
            return results

        persons = await dnr.get_group_persons(child.group_id)

        new_caches = []

        for person in persons:
            new_caches.append((
                cache_key_factory(person['id']),
                {'name': person['shortName']}
            ))
            if person['id'] in persons_id:
                results[person['id']] = person['shortName']

        await cache_repository.put_caches(session.session_id, new_caches)

        return results

    @classmethod
    async def _get_extracurricular_activities(
            cls, extracurricular_activity_repository: ExtracurricularActivityRepository,
            child: Child,
            period: tuple[datetime, datetime],
    ) -> dict[date, list[ScheduleExtracurricularActivity]]:
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
    def _calc_avg(cls, marks: list[MarkLog], others_marks: list[MarksOther]) -> MarkLog:
        sum_marks = 0
        count_marks = 0
        moods: dict[int, Literal["good", "average", "bad", "more"]] = {}

        for mark in marks:
            if (value := mark.value.replace('+', '').replace('-', '')).isnumeric():
                sum_marks += int(value)
                count_marks += 1
                moods[int(value)] = mark.mood

        for other_marks in others_marks:
            for mark in other_marks.marks:
                if (value := mark.value.replace('+', '').replace('-', '')).isnumeric():
                    sum_marks += int(value)
                    count_marks += 1
                    moods[int(value)] = mark.mood

        avg = MarkLog(
            value=str(value := round_or_int(sum_marks / count_marks)).replace('.', ','),
            mood=moods.get(int(value), MarkLog.default_mood()),
            work=None,
            created=None
        ) if count_marks != 0 else None

        return avg

    @classmethod
    def _get_lesson_url(cls, school_id: int, lesson_id: int) -> str:
        url = URL.build(
            scheme='https',
            host='schools.dnevnik.ru',
            path='/lesson',
            query={'school': school_id, 'lesson': lesson_id}
        )
        return str(url)

    async def getLessonRatingStats(self, session_id: str, rating_key: str) -> LessonRatingStatsApiResponse:
        async with self.uow_factory() as uow:
            try:
                params = rating_key.split('.')
                period_id = int(params[0], 36)
                subject_id = int(params[1], 36)
                lesson_date = datetime.fromisoformat(params[2]).date()
            except (ValueError, IndexError) as e:
                await uow.log_repository.add_log(path='getLessonRatingStats', session_id=session_id, status=False,
                                                 value=f"{e.__class__.__name__}: {e}")
                return LessonRatingStatsApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = parent.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                old, new = await self._get_change_avg(dnr, child, period_id, lesson_date, subject_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            await uow.statistic_repository.add_statistic(parent.parent_id, 'getLessonRatingStats')

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
        before, after = await gather(
            dnr.get_group_avg_marks_by_date(child.group_id, period_id, lesson_date - timedelta(days=1)),
            dnr.get_group_avg_marks_by_date(child.group_id, period_id, lesson_date)
        )

        old_avg: Optional[str] = None
        new_avg: Optional[str] = None

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

        old = MarkLog(
            mood=mark_moods.get(int(float(old_avg.replace(',', '.'))), MarkLog.default_mood()),
            value=old_avg,
            work=None,
            created=None
        ) if old_avg else None
        new = MarkLog(
            mood=mark_moods.get(int(float(new_avg.replace(',', '.'))), MarkLog.default_mood()),
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
        cache_key = "periods"

        now = datetime_now()

        if ((cache := await cache_repository.get_cache(session.session_id, cache_key)) and
                now - cache.created_at < timedelta(days=28)):
            return cache.value
        else:
            periods = await dnr.get_reporting_periods(child.group_id)
            await cache_repository.put_cache(session.session_id, cache_key, periods)

            return periods

    @classmethod
    async def _get_period(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            _date: date, periods: Optional[list[dict]] = None
    ) -> Optional[dict]:
        if periods is None:
            periods = await cls._get_periods(cache_repository, dnr, session, child)
            periods = sorted(periods, key=lambda p: datetime.fromisoformat(p['start']))

        return cls._get_active_period(periods, _date)

    @classmethod
    def _get_active_period(cls, periods: list[dict], _date: date) -> dict:
        active_period = None
        for number, period in enumerate(periods):
            start = datetime.fromisoformat(period['start']).date()

            if start > _date:
                active_period = periods[max(0, number - 1)]
                break
        if active_period is None:
            active_period = periods[-1]

        return active_period

    async def getMarks(self, session_id: str, last: int) -> MarksApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = parent.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            now = datetime_now(child.timezone)
            from_date = (now - timedelta(days=last)).date()

            try:
                recent_marks, (period_marks, active_period_id) = await gather(
                    self._get_recent_marks(uow.cache_repository, dnr, session, child, from_date, limit=20),
                    self._get_period_marks(uow.cache_repository, dnr, session, child)
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            await uow.statistic_repository.add_statistic(parent.parent_id, 'getMarks')

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
        recent_marks = await dnr.get_person_recent_marks(child.child_id, child.group_id, from_date, limit=limit)

        if not recent_marks:
            return []

        works = {work['id']: work for work in recent_marks['works']}
        subjects = {subject['id']: subject['name'] for subject in recent_marks['subjects']}

        periods: dict[int, dict] = {}

        work_types_id: set[int] = {mark['workType'] for mark in recent_marks['marks']}
        period_works: set[int] = {mark['work'] for mark in recent_marks['marks'] if mark['lesson'] is None}

        if period_works:
            work_types, _periods = await gather(
                cls._get_work_types(cache_repository, dnr, session, child, work_types_id),
                cls._get_periods(cache_repository, dnr, session, child)
            )
            periods = {_period['id']: _period for _period in _periods}
        else:
            work_types = await cls._get_work_types(cache_repository, dnr, session, child, work_types_id)

        marks: list[MarkLast] = []

        for mark in recent_marks['marks']:
            work = works[mark['work']]
            subject = subjects.get(work['subjectId'], "Неизвестный предмет")
            work_type = work_types.get(mark['workType'])

            period: Optional[str] = None

            if mark['lesson'] is None:
                if work['type'] == "PeriodMark":
                    period = periods[work['periodNumber']]['name']
                elif work['type'] == "Exam":
                    period = "Экзамен"
                elif work['type'] == "PeriodFinalMark":
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
        now = datetime_now(child.timezone).date()
        active_period = await cls._get_period(cache_repository, dnr, session, child, now)

        start = datetime.fromisoformat(active_period['start']).date()
        finish = datetime.fromisoformat(active_period['finish']).date()

        _marks, _avg_marks, final_marks = await gather(
            dnr.get_person_marks(child.child_id, child.group_id, start, finish),
            dnr.get_group_avg_marks(child.group_id, start, finish),
            dnr.get_person_final_marks(child.child_id, child.group_id)
        )

        avg_marks: dict[int, dict] = {}
        for person in _avg_marks:
            if person['person'] != child.child_id:
                continue

            for mark in person['per-subject-averages']:
                avg_marks[mark['subject']] = mark

        _lessons = await dnr.get_many_lessons([mark['lesson'] for mark in _marks])
        lessons = {lesson['id']: lesson for lesson in _lessons}

        marks: dict[int, list[dict]] = {}
        for mark in _marks:
            subject_id = lessons[mark['lesson']]['subject']['id']
            if marks.get(subject_id) is None:
                marks[subject_id] = []
            marks[subject_id].append(mark)

        subjects = {subject['id']: subject['name'] for subject in final_marks['subjects']}
        works = {work['id']: work for work in final_marks['works'] if work['periodNumber'] == active_period['number']}
        period_marks = {work['subjectId']: mark for mark in final_marks['marks'] if (work := works.get(mark['work']))}

        result = []
        result_without_marks = []
        for subject_id, subject in sorted(subjects.items(), key=lambda subject: subject[1]):
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
                    work=None,
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone),
                ) for mark in marks[subject_id]],
                averageMark=MarkLog(
                    value=value,
                    mood=mark_moods.get(round(float(value.replace(',', '.'))), MarkLog.default_mood()),
                    work=None,
                    created=None
                ) if (value := avg_marks.get(subject_id, {}).get('avg-mark-value')) else None,
                periodMark=MarkLog(
                    mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                    value=mark['textValue'],
                    work=None,
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                ) if (mark := period_marks.get(subject_id)) else None,
                ratingKey=f"{zip_int(subject_id)}.{zip_int(active_period['id'])}"
            ))

        result.extend(result_without_marks)

        return result, active_period['id']

    async def getMarksRatingStats(self, session_id: str, rating_key: str) -> MarksRatingStatsApiResponse:
        async with self.uow_factory() as uow:
            try:
                key_type = rating_key[0]
                entity_id = int(rating_key[1:], 36)
            except (ValueError, IndexError) as e:
                await uow.log_repository.add_log(path='getMarksRatingStats', session_id=session_id, status=False,
                                                 value=f"{e.__class__.__name__}: {e}")
                return MarksRatingStatsApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = parent.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            _highlighting_persons = await uow.highlighting_person_repository.get_highlighting_persons(parent.parent_id)
            highlighting_persons = {person.person_id for person in _highlighting_persons}

            if key_type == 'w':
                try:
                    marks = await dnr.get_marks_by_work(entity_id)
                except BaseDnevnikruException as e:
                    if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                        raise SessionError(session_id=session.session_id) from e
                    raise

                persons_id: set[int] = {mark['person'] for mark in marks}
                persons = await self._get_persons_name(uow.cache_repository, dnr, session, child, persons_id)

                marks = []
                others_marks = []
                for mark in marks:
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

                avg = self._calc_avg(marks, others_marks)

                await uow.statistic_repository.add_statistic(parent.parent_id, 'getMarksRatingStats')

                return MarksRatingStatsApiResponse(
                    answer=MarksRatingStatsResult(
                        othersMarks=sorted(
                            others_marks,
                            key=self._key_others_marks,
                            reverse=True
                        ),
                        avgGroupMark=avg,
                        oldAvgMark=None,
                        newAvgMark=None
                    )
                )

            # key_type == 'l'
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

            others_marks = sorted(
                others_marks.values(),
                key=self._key_others_marks,
                reverse=True
            )
            avg = self._calc_avg(marks, others_marks)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'getMarksRatingStats')

            return MarksRatingStatsApiResponse(
                answer=MarksRatingStatsResult(
                    othersMarks=others_marks,
                    avgGroupMark=avg,
                    oldAvgMark=old,
                    newAvgMark=new
                )
            )

    async def getMarksSubjectRating(self, session_id: str, rating_key: str) -> MarksSubjectRatingApiResponse:
        async with self.uow_factory() as uow:
            try:
                key = re.fullmatch(r'(?:(?P<subject_id>[0-9a-z]{1,13})\.)?(?P<period_id>[0-9a-z]{1,13})', rating_key)
                assert key
                subject_id = int(key.group('subject_id'), 36) if key.group('subject_id') else None
                period_id = int(key.group('period_id'), 36)
            except (ValueError, AssertionError) as e:
                await uow.log_repository.add_log(path='getMarksSubjectRating', session_id=session_id, status=False,
                                                 value=f"{e.__class__.__name__}: {e}; {rating_key}")
                return MarksSubjectRatingApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = parent.active_child

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                periods = await self._get_periods(uow.cache_repository, dnr, session, child)
                period = next(filter(lambda p: p['id'] == period_id, periods))

                start = datetime.fromisoformat(period['start']).date()
                finish = datetime.fromisoformat(period['finish']).date()
                avg_marks = await dnr.get_group_avg_marks(child.group_id, start, finish)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise
            except StopIteration as e:
                await uow.log_repository.add_log(path='getMarksSubjectRating', session_id=session_id, status=False,
                                                 value=f"{e.__class__.__name__}: {e}; {rating_key}")
                return MarksSubjectRatingApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неверный ratingKey"
                    )
                )

            persons_id: set[int] = {person['person'] for person in avg_marks}
            persons_name = await self._get_persons_name(uow.cache_repository, dnr, session, child, persons_id)

            _highlighting_person = await uow.highlighting_person_repository.get_highlighting_persons(parent.parent_id)
            highlighting_person = {person.person_id for person in _highlighting_person}

            class_rating: list[tuple[MarksOther, float, int]] = []

            if subject_id is None:
                for person in avg_marks:
                    if len(person['per-subject-averages']) == 0 or not (name := persons_name.get(person['person'])):
                        continue

                    sum_marks = sum(float(mark['avg-mark-value'].replace(',', '.')) for mark in person['per-subject-averages'])
                    avg_mark = round(sum_marks / len(person['per-subject-averages']), 2)

                    class_rating.append((MarksOther(
                        name=name,
                        personKey=zip_int(person['person']),
                        isHighlighting=person['person'] in highlighting_person,
                        marks=[MarkLog(
                            mood=mark_moods.get(round(avg_mark), MarkLog.default_mood()),
                            value=str(avg_mark).replace('.', ','),
                            work=None,
                            created=None
                        )]
                    ), avg_mark, person['person']))

            else:
                for person in avg_marks:
                    if not (name := persons_name.get(person['person'])):
                        continue

                    for subject in person['per-subject-averages']:
                        if subject['subject'] != subject_id:
                            continue

                        avg_mark = float(subject['avg-mark-value'].replace(',', '.'))

                        class_rating.append((MarksOther(
                            name=name,
                            personKey=zip_int(person['person']),
                            isHighlighting=person['person'] in highlighting_person,
                            marks=[MarkLog(
                                mood=mark_moods.get(round(avg_mark), MarkLog.default_mood()),
                                value=subject['avg-mark-value'],
                                work=None,
                                created=None
                            )]
                        ), avg_mark, person['person']))

            rating = sorted(class_rating, key=lambda r: (r[0].isHighlighting, r[1], r[2] == child.child_id), reverse=True)

            me: Optional[int] = None
            last_number = 0
            last_avg = None
            for i, person in enumerate(rating):
                if person[2] == child.child_id:
                    me = i
                if person[1] == last_avg:
                    person[0].number = last_number
                else:
                    person[0].number = i
                    last_number = i
                last_avg = person[1]

            old = await uow.rating_repository.get_rating(child.child_id, period_id, subject_id or -1)
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
            ) if old else None

            if me is not None:
                await uow.rating_repository.put_rating(child.child_id, period_id, subject_id or -1, me, rating[me][0].marks[0].value, rating[me][0].marks[0].mood)
            else:
                await uow.rating_repository.delete_rating(child.child_id, period_id, subject_id or -1)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'getMarksSubjectRating')

            return MarksSubjectRatingApiResponse(
                answer=MarksSubjectRatingResult(
                    rating=[item[0] for item in rating],
                    oldMark=old_mark if me and old_mark != rating[me][0] else None
                )
            )

    async def getFinalMarks(self, session_id: str) -> MarksFinalApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = parent.active_child

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
            subjects = {subject['id']: subject['name'] for subject in marks['subjects']}

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
                    work=None,
                    created=astimezone(datetime.fromisoformat(mark['date']).replace(tzinfo=UTC), child.timezone)
                )

            await uow.statistic_repository.add_statistic(parent.parent_id, 'getFinalMarksSubjectRating')

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
