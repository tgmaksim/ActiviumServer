from asyncio import gather
from typing import Union, Optional, Literal

from core import datetime_now
from datetime import date, timedelta, datetime

from database import Database

from dnevnikru import AioDnevnikruApi

from fastapi.background import BackgroundTasks

from api.core import Session, get_cache, get_caches, put_cache, put_caches
from .entities import (
    MarkLog,
    MarkLast,
    WorkType,
    MarksOther,
    MarkLog0x00000016,
    MarksSubjectPeriod,
    MarksOther0x00000021,
    ScheduleHomeworkDocument,
    ScheduleExtracurricularActivity,
)


__all__ = ['get_class_schedule', 'get_person_schedule', 'get_schedule_marks', 'get_extracurricular_activities',
           'get_recent_marks', 'get_period_marks']


async def get_class_schedule(
        session: Session,
        dnr: AioDnevnikruApi,
        background_tasks: BackgroundTasks,
        *,
        start_date: date,
        end_date: date
) -> list[dict]:
    """
    Получение расписания всего класса: всех подгрупп и профилей за период включительно. Сохраняется в кеш до полуночи

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param background_tasks: объект для добавления фоновых задач
    :param start_date: начало периода включительно
    :param end_date: конец периода включительно
    :return: расписание всего класса
    :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
    :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
    """

    cache_key = f"all_schedule|{start_date}|{end_date}"

    # Если в кеше актуальное (загруженное сегодня) расписание
    if ((cache := await get_cache(session.session, cache_key)) and
            (cache.datetime + timedelta(hours=session.timezone)).date() == datetime_now(session.timezone).date()):
        return cache.value
    else:
        class_schedule = await dnr.get_group_lessons(session.group_id, start_date, end_date)
        background_tasks.add_task(put_cache, session.session, cache_key, class_schedule)

        return class_schedule


async def get_person_schedule(
        session: Session,
        dnr: AioDnevnikruApi,
        *,
        start_date: date,
        end_date: date
) -> tuple[dict, dict[int, list[ScheduleHomeworkDocument]]]:
    """
    Получение расписания конкретно для обучающегося и прикрепленных файлов к домашним заданиям

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param start_date: начало периода включительно
    :param end_date: конец периода включительно
    :return: расписание и прикрепленные файлы к домашнему по идентификаторам уроков
    """

    schedule = await dnr.get_person_schedule(session.person_id, session.group_id, start_date, end_date)

    lessons_id = []
    homeworks_id = []
    for day in schedule['days']:
        for homework in day['homeworks']:
            lessons_id.append(homework['lesson'])
            homeworks_id.append(homework['id'])

    homeworks = await get_homeworks_files(dnr, homeworks_id=homeworks_id)

    return schedule, {lessons_id[i]: homeworks.get(homeworks_id[i], []) for i in range(len(homeworks_id))}


async def get_homeworks_files(
        dnr: AioDnevnikruApi,
        *,
        homeworks_id: list[int]
) -> dict[int, list[ScheduleHomeworkDocument]]:
    """
    Получение прикрепленных файлов к домашним заданиям

    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param homeworks_id: идентификаторы домашних заданий
    :return: списки прикрепленных файлов к домашним заданиям по идентификаторам
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


async def get_schedule_marks(
        session: Session,
        dnr: AioDnevnikruApi,
        background_tasks: BackgroundTasks,
        mark_type: type[Union[MarkLog, MarkLog0x00000016]],
        marks_other_type: type[Union[MarksOther0x00000021, MarksOther]],
        *,
        start_date: date,
        end_date: date
) -> tuple[dict[int, list[Union[MarkLog0x00000016, MarkLog]]], dict[int, list[Union[MarksOther0x00000021, MarksOther]]]]:
    """
    Получение своих оценок и оценок класса за период включительно

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param background_tasks: объект для добавления фоновых задач
    :param mark_type: версия класса MarkLog
    :param marks_other_type: версия класса MarksOther
    :param start_date: начало периода включительно
    :param end_date: конец периода включительно
    :return: свои оценки по урокам и оценки класса по урокам и по ученикам
    :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
    :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
    """

    my_marks = {}
    others_marks = {}

    marks = await dnr.get_group_marks(session.group_id, start_date, end_date)

    work_types_id = []
    persons_id = []
    for mark in marks:
        work_types_id.append(mark['workType'])
        persons_id.append(mark['person'])

    work_types, persons = await gather(
        get_work_types(session, dnr, background_tasks, work_types_id=work_types_id),
        get_persons_name(session, dnr, background_tasks, persons_id=persons_id)
    )

    for mark in marks:
        mood = mark['mood'].lower() if mark['mood'].lower() in mark_type.moods else mark_type.default_mood()

        if mark['person'] == session.person_id:
            if my_marks.get(mark['lesson']) is None:
                my_marks[mark['lesson']] = []

            my_marks[mark['lesson']].append(mark_type(
                mood=mood,
                value=mark['value'],
                work=work_types.get(mark['workType'])
            ))
        else:
            if others_marks.get(mark['lesson']) is None:
                others_marks[mark['lesson']] = {}
            if others_marks[mark['lesson']].get(mark['person']) is None:
                if not persons.get(mark['person']):
                    continue
                others_marks[mark['lesson']][mark['person']] = marks_other_type(
                    name=persons[mark['person']],
                    marks=[]
                )

            other = others_marks[mark['lesson']][mark['person']]
            other.marks.append(mark_type(
                value=mark['value'],
                mood=mood,
                work=work_types.get(mark['workType'])
            ))

    return my_marks, {lesson: list(others_marks[lesson].values()) for lesson in others_marks}


async def get_work_types(
        session: Session,
        dnr: AioDnevnikruApi,
        background_tasks: BackgroundTasks,
        *,
        work_types_id: list[int]
) -> dict[int, WorkType]:
    """
    Получение названия и аббревиатуры работы

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param background_tasks: объект для добавления фоновых задач
    :param work_types_id: идентификаторы типов работ в дневнике.ру
    :return: название работы, аббревиатура работы по идентификатору
    """

    if not work_types_id:
        return {}

    now = datetime_now(session.timezone)

    caches = await get_caches(session.session, list(map(lambda w: f"workType|{w}", work_types_id)))
    results = {int(cache.key.split("|")[1]): WorkType(
        title=cache.value.get('title'),
        abbr=cache.value.get('title')
    ) for key, cache in caches.items() if now - (cache.datetime + timedelta(hours=session.timezone)) < timedelta(days=28)}

    if len(results) == len(work_types_id):
        return results

    set_work_types_id = set(work_types_id)
    work_types = await dnr.get_work_types(session.gymnasium_id)

    cache_keys = []
    cache_values = []

    for work_type in work_types:
        cache_keys.append(f"workType|{work_type['id']}")
        cache_values.append({'title': work_type['title'], 'abbr': work_type['abbr']})
        if work_type['id'] in set_work_types_id:
            results[work_type['id']] = WorkType(
                title=work_type['title'],
                abbr=work_type['abbr']
            )

    background_tasks.add_task(put_caches, session.session, cache_keys, cache_values)

    return results


async def get_persons_name(
        session: Session,
        dnr: AioDnevnikruApi,
        background_tasks: BackgroundTasks,
        *,
        persons_id: list[int]
) -> dict[int, str]:
    """
    Получение имени person в дневнике.ру

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param background_tasks: объект для добавления фоновых задач
    :param persons_id: идентификаторы person'ов в дневнике.ру
    :return: имена person'ов в дневнике.ру по идентификаторам
    """

    now = datetime_now(session.timezone)

    caches = await get_caches(session.session, list(map(lambda p: f"person|{p}", persons_id)))
    results = {int(cache.key.split("|")[1]): cache.value.get('name') for key, cache in caches.items()
               if now - (cache.datetime + timedelta(hours=session.timezone)) < timedelta(days=28)}

    if len(results) == len(persons_id):
        return results

    set_persons_id = set(persons_id)
    persons = await dnr.get_group_persons(session.group_id)

    cache_keys = []
    cache_values = []

    for person in persons:
        cache_keys.append(f"workType|{person['id']}")
        cache_values.append({'name': person['shortName']})
        if person['id'] in set_persons_id:
            results[person['id']] = person['shortName']

    background_tasks.add_task(put_caches, session.session, cache_keys, cache_values)

    return results


async def get_extracurricular_activities(
        session: Session,
        days_hash: list[str]
) -> dict[str, list[ScheduleExtracurricularActivity]]:
    """
    Получение внеурочных занятий класса в дни по md5-хешам с предметом и кабинетом

    :param session: данные сессии
    :param days_hash: md5-хеши отсортированного списка идентификаторов предметов
    :return: список внеурочных занятий
    """

    sql = ("SELECT day, subject, place FROM extracurricular_activities "
           "WHERE gymnasium_id = $1 AND group_id = $2 AND day = ANY($3::text[])")
    extracurricular_activities = await Database.fetch_all(sql, session.gymnasium_id, session.group_id, days_hash)

    results = {}
    for extracurricular_activity in extracurricular_activities:
        if results.get(extracurricular_activity['day']) is None:
            results[extracurricular_activity['day']] = []

        results[extracurricular_activity['day']].append(ScheduleExtracurricularActivity(
            subject=extracurricular_activity['subject'],
            place=str(extracurricular_activity['place']),
        ))

    return results


async def get_recent_marks(
        session: Session,
        dnr: AioDnevnikruApi,
        background_tasks: BackgroundTasks,
        *,
        from_date: date,
        limit: int
) -> list[MarkLast]:
    """
    Получение последних оценок по дате выставления и оценок класса за те же уроки

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param background_tasks: объект для добавления фоновых задач
    :param from_date: от какой даты получить оценки
    :param limit: лимит оценок для каждого предмета отдельно
    :return: список последних оценок по дате выставления и оценок класса за те же уроки
    """

    recent_marks = await dnr.get_person_recent_marks(session.person_id, session.group_id, from_date, limit=limit)

    if not recent_marks:
        return []

    works = {work['id']: work for work in recent_marks['works']}
    subjects = {subject['id']: subject['name'] for subject in recent_marks['subjects']}

    periods: dict[int, dict] = {}
    period_marks: dict[int, dict[int, dict]] = {}

    work_types_id: list[int] = [mark['workType'] for mark in recent_marks['marks']]
    lessons: list[int] = [mark['lesson'] for mark in recent_marks['marks'] if mark['lesson'] is not None]
    period_works: list[int] = [mark['work'] for mark in recent_marks['marks'] if mark['lesson'] is None]

    if period_works:
        work_types, (_lesson_marks, persons_name), periods, period_marks = await gather(
            get_work_types(session, dnr, background_tasks, work_types_id=work_types_id),
            get_many_marks(session, dnr, background_tasks, lessons=lessons),
            get_periods(session, dnr, background_tasks),
            get_marks_by_works(dnr, period_works)
        )
    else:
        work_types, (_lesson_marks, persons_name) = await gather(
            get_work_types(session, dnr, background_tasks, work_types_id=work_types_id),
            get_many_marks(session, dnr, background_tasks, lessons=lessons),
        )

    lesson_marks: dict[int, dict[int, list[dict]]] = {}
    for mark in _lesson_marks:
        if lesson_marks.get(mark['lesson']) is None:
            lesson_marks[mark['lesson']] = {}
        if lesson_marks[mark['lesson']].get(mark['person']) is None:
            lesson_marks[mark['lesson']][mark['person']] = []
        lesson_marks[mark['lesson']][mark['person']].append(mark)

    marks = []

    for mark in recent_marks['marks']:
        work = works[mark['work']]
        subject = subjects.get(work['subjectId'], "Предмет")
        work_type = work_types.get(mark['workType'])

        period: Optional[str] = None
        others_marks = lesson_marks.get(mark['lesson'], {})

        if mark['lesson'] is None:
            others_marks = period_marks.get(work['id'], {})

            if work['type'] == "PeriodMark":
                period = periods[work['periodNumber']]['name']
            elif work['type'] == "Exam":
                period = "Экзамен"
            elif work['type'] == "PeriodFinalMark":
                period = "Итоговая"

            if period:
                work_type = WorkType(title=period, abbr=period)

        lesson_date = datetime.fromisoformat(work['targetDate']).date()  # Дата урока
        lesson_date_format = None if period else lesson_date.strftime("%e %b.").strip()
        sent_date = datetime.fromisoformat(mark['date']) + timedelta(hours=session.timezone)  # Дата выставления

        marks.append(MarkLast(
            mark=MarkLog(
                value=mark['value'],
                mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                work=work_type
            ),
            work=work_type,
            subject=subject,
            sentDatetime=sent_date,
            lessonDate=lesson_date,
            lessonDateFormat=lesson_date_format,
            othersMarks=[MarksOther(
                name=name,
                marks=[MarkLog(
                    value=other_mark['value'],
                    mood=other_mark['mood'].lower() if other_mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                    work=work_type
                ) for other_mark in other_marks]
            ) for person_id, other_marks in others_marks.items() if (name := persons_name.get(person_id)) and person_id != session.person_id]
        ))

    return marks


async def get_periods(
        session: Session,
        dnr: AioDnevnikruApi,
        background_tasks: BackgroundTasks
) -> dict[int, dict]:
    """
    Получение названия отчетного периода

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param background_tasks: объект для добавления фоновых задач
    :return: названия отчетных периодов по номерам (periodNumber)
    """

    cache_key = "periods"
    now = datetime_now(session.timezone)

    if ((cache := await get_cache(session.session, cache_key)) and
            now - (cache.datetime + timedelta(hours=session.timezone)) < timedelta(days=28)):
        periods = cache.value
    else:
        periods = await dnr.get_reporting_periods(session.group_id)
        background_tasks.add_task(put_cache, session.session, cache_key, periods)

    periods = {period['number']: period for period in periods}

    return periods


async def get_marks_by_works(dnr: AioDnevnikruApi, works_id: list[int]) -> dict[int, dict[int, list[dict]]]:
    """
    Получение оценок класса за работы

    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param works_id: идентификаторы работ
    :return: оценки класса по работам и ученика
    """

    marks: list[list[dict]] = await gather(*(dnr.get_marks_by_work(work) for work in works_id))

    results = {}
    for i in range(len(works_id)):
        results[works_id[i]] = {}
        for mark in marks[i]:
            if results[works_id[i]].get(mark['person']) is None:
                results[works_id[i]][mark['person']] = []
            results[works_id[i]][mark['person']].append(mark)

    return results


async def get_many_marks(
        session: Session,
        dnr: AioDnevnikruApi,
        background_tasks: BackgroundTasks,
        *,
        lessons: list[int]
) -> tuple[list[dict], dict[int, str]]:
    """
    Получение оценок класса на уроках и имен одноклассников

    :param session: данные сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param background_tasks: объект для добавления фоновых задач
    :param lessons: идентификаторы уроков
    :return: список оценок класса и имена одноклассников по идентификаторам
    """

    if not lessons:
        return [], {}

    marks = await dnr.get_many_marks(lessons)
    persons_id = [mark['person'] for mark in marks]
    persons_name = await get_persons_name(session, dnr, background_tasks, persons_id=persons_id)

    return marks, persons_name


async def get_period_marks(session: Session, dnr: AioDnevnikruApi, background_tasks: BackgroundTasks):
    periods = await get_periods(session, dnr, background_tasks)

    active_period: Optional[int] = None
    for number, period in sorted(iter(periods.items())):
        if datetime.fromisoformat(period['start']) > datetime_now(session.timezone):
            active_period = max(0, number - 1)
            break
    if active_period is None:
        active_period = len(periods) - 1

    start = datetime.fromisoformat(periods[active_period]['start']).date()
    finish = datetime.fromisoformat(periods[active_period]['finish']).date()

    _avg_marks, final_marks = await gather(
        dnr.get_group_avg_marks(session.group_id, start, finish),
        dnr.get_person_final_marks(session.person_id, session.group_id)
    )

    avg_marks: dict[int, dict[int, dict]] = {}
    persons_id = []
    for person in _avg_marks:
        persons_id.append(person['person'])
        for mark in person['per-subject-averages']:
            if avg_marks.get(mark['subject']) is None:
                avg_marks[mark['subject']] = {}
            avg_marks[mark['subject']][person['person']] = mark

    subjects = {subject['id']: subject['name'] for subject in final_marks['subjects']}
    works = {work['id']: work for work in final_marks['works'] if work['periodNumber'] == active_period}
    period_marks = {work['subjectId']: mark for mark in final_marks['marks'] if (work := works.get(mark['work']))}

    persons_name, marks = await gather(
        get_persons_name(session, dnr, background_tasks, persons_id=persons_id),
        get_person_marks(session, dnr, subjects=list(subjects.keys()), start_date=start, end_date=finish)
    )

    # По-другому никак...
    mark_moods: dict[str, Literal["good", "average", "bad", "more"]] = \
        {"5": "good", "4": "good", "3": "average", "2": "bad", "1": "bad"}

    result = []
    for subject_id, subject in sorted(subjects.items(), key=lambda subject: subject[1]):
        if not marks[subject_id]:
            continue

        result.append(MarksSubjectPeriod(
            subject=subject,
            marks=[MarkLog(
                mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                value=mark['value'],
                work=None
            ) for mark in marks[subject_id]],
            averageMark=MarkLog(
                value=value,
                mood=mark_moods.get(str(int(float(value.replace(',', '.')))), "more"),
                work=None
            ) if (value := avg_marks.get(subject_id, {}).get(session.person_id, {}).get('avg-mark-value')) else None,
            periodMark=MarkLog(
                mood=mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                value=mark['value'],
                work=None
            ) if (mark := period_marks.get(subject_id)) else None,
            othersAverageMark=[MarksOther(
                name=name,
                marks=[MarkLog(
                    mood=mark_moods.get(str(int(float(mark['avg-mark-value'].replace(',', '.')))), "more"),
                    value=mark['avg-mark-value'],
                    work=None
                )]
            ) for person, mark in avg_marks.get(subject_id, {}).items() if (name := persons_name.get(person))]
        ))

    class_rating = []
    for person in _avg_marks:
        if len(person['per-subject-averages']) == 0 or not (name := persons_name.get(person['person'])):
            continue

        sum_marks = sum(float(mark['avg-mark-value'].replace(',', '.')) for mark in person['per-subject-averages'])
        avg_mark = round(sum_marks / len(person['per-subject-averages']), 2)

        class_rating.append((MarksOther(
            name=name,
            marks=[MarkLog(
                mood=mark_moods.get(str(int(avg_mark)), "more"),
                value=str(avg_mark).replace('.', ','),
                work=None
            )]
        ), avg_mark))

    return result, list(rating[0] for rating in sorted(class_rating, key=lambda r: r[1], reverse=True))


async def get_person_marks(
        session: Session,
        dnr: AioDnevnikruApi,
        *,
        subjects: list[int],
        start_date: date,
        end_date: date
) -> dict[int, list[dict]]:
    marks = await gather(*[dnr.get_person_marks(session.person_id, subject, start_date, end_date) for subject in subjects])

    return {subject: marks[i] for i, subject in enumerate(subjects)}
