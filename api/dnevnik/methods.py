from hashlib import md5
from typing import Union
from datetime import timedelta, datetime, date

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from core import log, get_bells_schedule, datetime_now
from api.core import (
    Session,
    get_cache,
    put_cache,
    get_session,
    SessionError,
    check_auth_session,
    assert_check_session,
    assert_check_api_key,
)

from . functions import get_homeworks_files, get_extracurricular_activities
from . entities import (
    MarkLog,
    MarksOther,
    ScheduleDay,
    ScheduleHours,
    ScheduleResult,
    ScheduleLesson,
    ScheduleApiRequest,
    ScheduleApiResponse,
    ScheduleDay0x00000012,
    ScheduleLesson0x00000011,
    ScheduleResult0x00000013,
    ScheduleResult0x00000019,
    ScheduleApiRequest0x00000022,
    ScheduleApiRequest0x00000015,
    ScheduleApiRequest0x0000000D,
    ScheduleApiResponse0x00000014,
    ScheduleApiResponse0x00000020,
)


router = APIRouter(prefix=f"/dnevnik", tags=["Dnevnik"])
__all__ = ['router']

REQUEST_DATA_TYPE = Union[ScheduleApiRequest0x0000000D, ScheduleApiRequest0x00000015,
                          ScheduleApiRequest0x00000022, ScheduleApiRequest]


@router.post(
    f"/getSchedule/{ScheduleApiRequest0x0000000D.classId}",
    summary="Получение расписания",
    description="Получение расписания на 2 недели (15 дней) с домашними заданиями и внеурочными занятиям. "
                f"Устаревший метод в пользу {ScheduleApiRequest.classId}",
    response_model=ScheduleApiResponse0x00000014,
    response_class=JSONResponse,
    status_code=200,
    deprecated=True,
)
async def _getSchedule0x0000000D(request: Request, request_data: ScheduleApiRequest0x0000000D):
    return await getScheduleRequest(request, request_data)


@router.post(
    f"/getSchedule/{ScheduleApiRequest0x00000015.classId}",
    summary="Получение расписания",
    description="Получение расписания на 2 недели (15 дней) с домашними заданиями, внеурочными занятиями и "
                "оценками с отметками о посещаемости за сегодняшний день. "
                f"Устаревший метод в пользу {ScheduleApiRequest.classId}",
    response_model=ScheduleApiResponse0x00000020,
    response_class=JSONResponse,
    status_code=200,
    deprecated=True
)
async def _getSchedule0x00000015(request: Request, request_data: ScheduleApiRequest0x00000015):
    return await getScheduleRequest(request, request_data)


@router.post(
    f"/getSchedule/{ScheduleApiRequest0x00000022.classId}",
    summary="Получение расписания",
    description="Получение расписания на 3 недели (22 дня): 7 дней до сегодня, сегодня и 15 дней после — "
                "с домашними заданиями, внеурочными занятиями и оценками с отметками о посещаемости. "
                f"Устаревший метод в пользу {ScheduleApiRequest.classId}",
    response_model=ScheduleApiResponse0x00000020,
    response_class=JSONResponse,
    status_code=200,
    deprecated=True
)
async def _getSchedule0x00000022(request: Request, request_data: ScheduleApiRequest0x00000022):
    return await getScheduleRequest(request, request_data)


@router.post(
    f"/getSchedule/{ScheduleApiRequest.classId}",
    summary="Получение расписания",
    description="Получение расписания на несколько дней с домашними заданиями, внеурочными занятиями и "
                "оценками с отметками о посещаемости",
    response_model=ScheduleApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def _getSchedule(request: Request, request_data: ScheduleApiRequest):
    return await getScheduleRequest(request, request_data)


async def getScheduleRequest(request: Request, request_data: REQUEST_DATA_TYPE):
    await assert_check_api_key(request_data.apiKey)
    await assert_check_session(request_data.data.session, check_auth=False)

    session = await get_session(request_data.data.session)
    now_date = datetime_now(session.timezone).date()

    if request_data.classId == ScheduleApiRequest0x0000000D.classId: response_type = ScheduleApiResponse0x00000014
    elif request_data.classId == ScheduleApiRequest.classId: response_type = ScheduleApiResponse
    else: response_type = ScheduleApiResponse0x00000020

    if response_type.classId == ScheduleApiResponse0x00000014.classId: answer_type = ScheduleResult0x00000013
    elif response_type.classId == ScheduleApiResponse0x00000020.classId: answer_type = ScheduleResult0x00000019
    else: answer_type = ScheduleResult

    if answer_type.classId == ScheduleResult0x00000013.classId: day_type = ScheduleDay0x00000012
    else: day_type = ScheduleDay

    if day_type.classId == ScheduleDay0x00000012.classId: lesson_type = ScheduleLesson0x00000011
    else: lesson_type = ScheduleLesson

    if request_data.classId in (ScheduleApiRequest0x0000000D.classId, ScheduleApiRequest0x00000015.classId): start_date = now_date
    elif request_data.classId == ScheduleApiRequest0x00000022.classId: start_date = now_date - timedelta(days=7)
    else: start_date = now_date - timedelta(days=request_data.data.before)

    if request_data.classId == ScheduleApiRequest.classId: end_date = now_date + timedelta(days=request_data.data.after)
    else: end_date = now_date + timedelta(days=14)

    # Расписание конкретно для пользователя
    try:
        person_schedule = await get_person_schedule(session, start_date, end_date)
    except AsyncDiaryError as e:
        if not await check_auth_session(session.session, dnevnik_token=session.dnevnik_token, person_id=session.person_id):
            raise SessionError(session=session.session)
        raise e from e

    # Расписание всего класса: всех подгрупп и профилей
    class_schedule = await get_class_schedule(session, start_date, end_date)

    logs = {}
    other_marks = {}

    if request_data.classId == ScheduleApiRequest0x00000015.classId:
        logs, other_marks = await get_schedule_logs(session, now_date, now_date, other=False)
    elif request_data.classId == ScheduleApiRequest0x00000022.classId:
        logs, other_marks = await get_schedule_logs(session, start_date, end_date, other=False)
    elif request_data.classId == ScheduleApiRequest.classId:
        logs, other_marks = await get_schedule_logs(session, start_date, end_date, other=True)

    result = []
    for day in person_schedule['days']:
        lessons = []

        day_date = datetime.strptime(day['date'], '%Y-%m-%dT%H:%M:%S')
        bells_schedule = get_bells_schedule(day_date)  # TODO: брать из базы данных

        for lesson in sorted(day['lessons'], key=lambda l: l['number']):
            files = []
            try:
                homework_id = map(lambda h: h['id'],
                                  filter(lambda h: h['lesson'] == lesson['id'] and h['files'],
                                         day['homeworks'])).__next__()
                files = await get_homeworks_files(session.dnevnik_token, homework_id)
            except AsyncDiaryError as e:
                await log(request, request.url.path, session.session, f"{e.__class__.__name__}: {e}")
            except StopIteration:
                pass

            try:
                subject = filter(lambda s: s['id'] == lesson['subjectId'], day['subjects']).__next__()['name']
            except (StopIteration, KeyError):
                subject = "Неизвестный урок"

            try:
                homework = '\n'.join(
                    map(lambda h: h['text'],
                        filter(lambda h: h['lesson'] == lesson['id'], day['homeworks'])))
            except KeyError:
                homework = None

            lessons.append(lesson_type(
                number=lesson['number'] - 1,  # Начало с 0
                subject=subject,
                place=lesson['place'],
                hours=ScheduleHours(**bells_schedule[lesson['number'] - 1]),
                logs=logs.get(lesson['id'], []),
                othersMarks=other_marks.get(lesson['id'], []),
                homework=homework or None,
                files=files
            ))

        # Получение md5-хеша расписания на день:
        # отсортированный список из id предметов всего класса на данный день
        day_hash = md5(
            str(
                sorted(
                    map(
                        lambda l: l['subject']['id'],
                        filter(
                            lambda l: l['date'] == day['date'],
                            class_schedule
                        )
                    )
                )
            ).encode('utf-8')
        ).hexdigest()

        # Используя полученный md5, можно получить внеурочные занятия класса
        extracurricular_activities = await get_extracurricular_activities(
            session.gymnasium_id, session.group_id, day_date.weekday(), day_hash)
        hours_extracurricular_activities = bells_schedule[len(lessons)] if extracurricular_activities else None

        result.append(day_type(
            date=day_date.date().strftime('%Y-%m-%d'),
            lessons=lessons,
            hoursExtracurricularActivities=hours_extracurricular_activities,
            extracurricularActivities=extracurricular_activities
        ))

    await log(request, request.url.path, session.session, "200 OK")
    return response_type(
        status=True,
        answer=answer_type(
            schedule=result,
            timezone=session.timezone
        )
    )


async def get_person_schedule(session: Session, start_date: date, end_date: date) -> dict:
    """
    Получение расписания конкретно для пользователя за период включительно

    :param session: данные сессии
    :param start_date: начало периода включительно
    :param end_date: конец периода включительно
    :except AsyncDiaryError: ошибка запроса в дневник.ру
    :return: расписание
    """

    cache_key = f"schedule|{start_date}|{end_date}"

    # Если в кеше актуальное (загруженное сегодня) расписание
    if ((cache := await get_cache(session.session, cache_key)) and
            (cache.datetime + timedelta(hours=session.timezone)).date() == datetime_now(session.timezone).date()):
        return cache.value
    else:
        async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
            # Расписание конкретно для пользователя
            person_schedule = await dn.get_person_schedule(
                session.person_id,
                session.group_id,
                str(start_date),
                str(end_date)
            )

        await put_cache(session.session, cache_key, person_schedule)

        return person_schedule


async def get_class_schedule(session: Session, start_date: date, end_date: date) -> dict:
    """
    Получение расписания всего класса: всех подгрупп и профилей за период включительно

    :param session: данные сессии
    :param start_date: начало периода включительно
    :param end_date: конец периода включительно
    :except AsyncDiaryError: ошибка запроса в дневник.ру
    :return: расписание
    """

    cache_key = f"all_schedule|{start_date}|{end_date}"

    # Если в кеше актуальное (загруженное сегодня) расписание
    if ((cache := await get_cache(session.session, cache_key)) and
            (cache.datetime + timedelta(hours=session.timezone)).date() == datetime_now(session.timezone).date()):
        return cache.value
    else:
        async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
            # Расписание всего класса: всех подгрупп и профилей
            class_schedule = await dn.get_group_lessons_info(
                session.group_id,
                str(start_date),
                str(end_date)
            )

        await put_cache(session.session, cache_key, class_schedule)

        return class_schedule


async def get_schedule_logs(session: Session, start_date: date, end_date: date, other: bool) -> tuple[dict, dict]:
    """
    Получение своих оценок и отметок о посещаемости уроков и оценок класса за период включительно

    :param session: данные сессии
    :param start_date: начало периода включительно
    :param end_date: конец периода включительно
    :param other: получать оценки других
    :except AsyncDiaryError: ошибка запроса в дневник.ру
    :return: свои оценки и отметки о посещаемости уроков и оценки класса
    """

    logs = {}
    other_marks = {}

    names = {}

    async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
        if other:
            marks = await dn.get_group_marks_period(session.group_id, start_date, end_date)
        else:
            marks = await dn.get(f"persons/{session.person_id}/edu-groups/{session.group_id}/marks/{start_date}/{end_date}")

    for mark in marks:
        mood = mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods() else MarkLog.default_mood()

        if mark['person'] == session.person_id:
            if logs.get(mark['lesson']) is None:
                logs[mark['lesson']] = []

            logs[mark['lesson']].append(MarkLog(
                mood=mood,
                value=mark['value']
            ))
        else:
            if other_marks.get(mark['lesson']) is None:
                other_marks[mark['lesson']] = {}
            if names.get(mark['person']) is None:
                names[mark['person']] = await get_person_name(session, mark['person'])
            if other_marks[mark['lesson']].get(mark['person']) is None:
                other_marks[mark['lesson']][mark['person']] = MarksOther(
                    name=names[mark['person']],
                    marks=[]
                )

            other = other_marks[mark['lesson']][mark['person']]
            other.marks.append(MarkLog(
                value=mark['value'],
                mood=mood
            ))

    async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
        lesson_logs = (await dn.get_person_lesson_logs(session.person_id, str(start_date), str(end_date)))['logEntries']

    for lesson_log in lesson_logs:
        if logs.get(lesson_log['lesson']) is None:
            logs[lesson_log['lesson']] = []

        if value := MarkLog.log_value(lesson_log['status']):
            logs[lesson_log['lesson']].append(MarkLog(
                mood=MarkLog.default_mood(),
                value=value
            ))

    return logs, {lesson: other_marks[lesson].values() for lesson in other_marks}


async def get_person_name(session: Session, person_id: int) -> str:
    """
    Получение имени person в дневнике.ру

    :param session: данные сессии
    :param person_id: идентификатор person в дневнике.ру
    :return: имя person в дневнике.ру
    """

    cache_key = f"person|{person_id}"
    person_name = "Неизвестный"

    if ((cache := await get_cache(session.session, cache_key)) and
            datetime_now(session.timezone) - (cache.datetime + timedelta(hours=session.timezone)) < timedelta(days=28)):
        return cache.value['name']
    else:
        try:
            async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
                persons = await dn.get_group_persons(session.group_id)

        except AsyncDiaryError:
            await log(None, None, session.session, "Error getting person info")
            return person_name

        for person in persons:
            if person['id'] == person_id:
                person_name = person['shortName']

            await put_cache(session.session, f"person|{person['id']}", {'name': person['shortName']})

        return person_name
