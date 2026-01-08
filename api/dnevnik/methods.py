from hashlib import md5
from typing import Union
from asyncio import gather
from datetime import timedelta, datetime, date

from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi.background import BackgroundTasks

from dnevnikru import AioDnevnikruApi, BaseDnevnikruException

from core import log, get_bells_schedule, datetime_now, httpx_client
from api.core import (
    get_session,
    SessionError,
    check_auth_session,
    assert_check_session,
    assert_check_api_key,
)

from .functions import (
    get_schedule_marks,
    get_class_schedule,
    get_person_schedule,
    get_extracurricular_activities
)
from . entities import (
    MarkLog,
    MarksOther,
    ScheduleDay,
    ScheduleHours,
    ScheduleResult,
    ScheduleLesson,
    MarkLog0x00000016,
    ScheduleApiRequest,
    ScheduleApiResponse,
    MarksOther0x00000021,
    ScheduleDay0x00000012,
    ScheduleDay0x00000018,
    ScheduleLesson0x00000011,
    ScheduleLesson0x00000017,
    ScheduleHomeworkDocument,
    ScheduleResult0x00000013,
    ScheduleResult0x00000019,
    ScheduleResult0x00000026,
    ScheduleApiRequest0x00000023,
    ScheduleApiRequest0x00000022,
    ScheduleApiRequest0x00000015,
    ScheduleApiRequest0x0000000D,
    ScheduleApiResponse0x00000014,
    ScheduleApiResponse0x00000020,
    ScheduleApiResponse0x00000027,
)

from . functions import get_recent_marks, get_period_marks
from . entities import (
    MarksResult,
    MarksApiRequest,
    MarksApiResponse
)


__all__ = ['router']

router = APIRouter(prefix="/dnevnik", tags=["Dnevnik"])

type ScheduleRequestDataType = Union[ScheduleApiRequest0x0000000D, ScheduleApiRequest0x00000015,
                                     ScheduleApiRequest0x00000022, ScheduleApiRequest0x00000023, ScheduleApiRequest]


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
async def _getSchedule0x0000000D(request: Request, request_data: ScheduleApiRequest0x0000000D, background_tasks: BackgroundTasks):
    return await getScheduleRequest(request, request_data, background_tasks)


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
async def _getSchedule0x00000015(request: Request, request_data: ScheduleApiRequest0x00000015, background_tasks: BackgroundTasks):
    return await getScheduleRequest(request, request_data, background_tasks)


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
async def _getSchedule0x00000022(request: Request, request_data: ScheduleApiRequest0x00000022, background_tasks: BackgroundTasks):
    return await getScheduleRequest(request, request_data, background_tasks)


@router.post(
    f"/getSchedule/{ScheduleApiRequest0x00000023.classId}",
    summary="Получение расписания",
    description="Получение расписания на несколько дней с домашними заданиями, внеурочными занятиями и "
                f"оценками с отметками о посещаемости. Устаревший метод в пользу {ScheduleApiRequest.classId}",
    response_model=ScheduleApiResponse0x00000027,
    response_class=JSONResponse,
    status_code=200,
    deprecated=True
)
async def _getSchedule0x00000023(request: Request, request_data: ScheduleApiRequest0x00000023, background_tasks: BackgroundTasks):
    return await getScheduleRequest(request, request_data, background_tasks)


@router.post(
    f"/getSchedule/{ScheduleApiRequest.classId}",
    summary="Получение расписания",
    description="Получение расписания на несколько дней с домашними заданиями, внеурочными занятиями и "
                "оценками класса с отметками о посещаемости",
    response_model=ScheduleApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def _getSchedule(request: Request, request_data: ScheduleApiRequest, background_tasks: BackgroundTasks):
    return await getScheduleRequest(request, request_data, background_tasks)


async def getScheduleRequest(request: Request, request_data: ScheduleRequestDataType, background_tasks: BackgroundTasks):
    await gather(
        assert_check_api_key(request_data.apiKey),
        assert_check_session(request_data.data.session, check_auth=False)
    )

    session = await get_session(request_data.data.session)
    dnr = AioDnevnikruApi(client=httpx_client, token=session.dnevnik_token)
    now_date = datetime_now(session.timezone).date()

    response_type: type[Union[ScheduleApiResponse0x00000014, ScheduleApiResponse0x00000020,
                        ScheduleApiResponse0x00000027, ScheduleApiResponse]]
    if request_data.classId == ScheduleApiRequest0x0000000D.classId: response_type = ScheduleApiResponse0x00000014
    elif request_data.classId == ScheduleApiRequest0x00000015.classId: response_type = ScheduleApiResponse0x00000020
    elif request_data.classId == ScheduleApiRequest0x00000022.classId: response_type = ScheduleApiResponse0x00000020
    elif request_data.classId == ScheduleApiRequest0x00000023.classId: response_type = ScheduleApiResponse0x00000027
    else: response_type = ScheduleApiResponse

    answer_type: type[Union[ScheduleResult0x00000013, ScheduleResult0x00000019, ScheduleResult0x00000026, ScheduleResult]]
    if response_type.classId == ScheduleApiResponse0x00000014.classId: answer_type = ScheduleResult0x00000013
    elif response_type.classId == ScheduleApiResponse0x00000020.classId: answer_type = ScheduleResult0x00000019
    elif response_type.classId == ScheduleApiResponse0x00000027.classId: answer_type = ScheduleResult0x00000026
    else: answer_type = ScheduleResult

    day_type: type[Union[ScheduleDay0x00000012, ScheduleDay0x00000018, ScheduleDay]]
    if answer_type.classId == ScheduleResult0x00000013.classId: day_type = ScheduleDay0x00000012
    elif answer_type.classId == ScheduleResult0x00000019.classId: day_type = ScheduleDay0x00000018
    elif answer_type.classId == ScheduleResult0x00000026.classId: day_type = ScheduleDay0x00000018
    else: day_type = ScheduleDay

    lesson_type: type[Union[ScheduleLesson0x00000011, ScheduleLesson0x00000017, ScheduleLesson]]
    if day_type.classId == ScheduleDay0x00000012.classId: lesson_type = ScheduleLesson0x00000011
    elif day_type.classId == ScheduleDay0x00000018.classId: lesson_type = ScheduleLesson0x00000017
    else: lesson_type = ScheduleLesson

    mark_type: type[Union[MarkLog0x00000016, MarkLog]]
    if lesson_type.classId == ScheduleLesson0x00000011.classId: mark_type = MarkLog0x00000016  # Не используется
    elif lesson_type.classId == ScheduleLesson0x00000017.classId: mark_type = MarkLog0x00000016
    else: mark_type = MarkLog

    marks_other_type: type[Union[MarksOther0x00000021, MarksOther]]
    if lesson_type.classId == ScheduleLesson0x00000011.classId: marks_other_type = MarksOther0x00000021  # Не используется
    elif lesson_type.classId == ScheduleLesson0x00000017.classId: marks_other_type = MarksOther0x00000021
    else: marks_other_type = MarksOther

    start_date: date
    if request_data.classId == ScheduleApiRequest0x0000000D.classId: start_date = now_date
    elif request_data.classId == ScheduleApiRequest0x00000015.classId: start_date = now_date
    elif request_data.classId == ScheduleApiRequest0x00000022.classId: start_date = now_date
    elif request_data.classId == ScheduleApiRequest0x00000023.classId: start_date = now_date - timedelta(days=request_data.data.before)
    else: start_date = now_date - timedelta(days=request_data.data.before)

    end_date: date
    if request_data.classId == ScheduleApiRequest0x0000000D.classId: end_date = now_date + timedelta(days=14)
    elif request_data.classId == ScheduleApiRequest0x00000015.classId: end_date = now_date + timedelta(days=14)
    elif request_data.classId == ScheduleApiRequest0x00000022.classId: end_date = now_date + timedelta(days=14)
    elif request_data.classId == ScheduleApiRequest0x00000023.classId: end_date = now_date + timedelta(days=request_data.data.after)
    else: end_date = now_date + timedelta(days=request_data.data.after)

    class_schedule: list[dict]  # расписание всего класса: всех подгрупп и профилей
    person_schedule: dict  # расписание конкретно для обучающегося
    files: dict[int, list[ScheduleHomeworkDocument]]  # прикрепленные файлы к домашнему заданию по идентификаторам уроков
    marks: dict[int, list[Union[MarkLog0x00000016, MarkLog]]]  # оценки по урокам
    others_marks: dict[int, list[Union[MarksOther0x00000021, MarksOther]]]  # оценки класса по урокам и обучающимся

    try:
        class_schedule, (person_schedule, files), (marks, others_marks) = await gather(
            get_class_schedule(session, dnr, background_tasks, start_date=start_date, end_date=end_date),
            get_person_schedule(session, dnr, start_date=start_date, end_date=end_date),
            get_schedule_marks(session, dnr, background_tasks, mark_type, marks_other_type, start_date=start_date, end_date=end_date)
        )
    except BaseDnevnikruException as e:
        if not await check_auth_session(session.session, dnr, dnevnik_token=session.dnevnik_token, person_id=session.person_id):
            raise SessionError(session=session.session) from e
        raise

    class_days_schedule: dict[str, list[dict]] = {}
    for lesson in class_schedule:
        if class_days_schedule.get(lesson['date']) is None:
            class_days_schedule[lesson['date']] = []
        class_days_schedule[lesson['date']].append(lesson)

    days_hash: dict[str, str] = {}
    for day in class_days_schedule:
        days_hash[day] = md5(str(sorted([lesson['subject']['id'] for lesson in class_days_schedule[day]])).encode()).hexdigest()

    extracurricular_activities = await get_extracurricular_activities(session, list(days_hash.values()))

    result = []
    for day in person_schedule['days']:
        subjects = {subject['id']: subject['name'] for subject in day['subjects']}
        homeworks: dict[int, list[str]] = {}
        for homework in day['homeworks']:
            if homeworks.get(homework['lesson']) is None:
                homeworks[homework['lesson']] = []
            homeworks[homework['lesson']].append(homework['text'])
        logs = {lesson_log['lesson']: [mark_type(
            mood=mark_type.default_mood(),
            value=value,
            work=None
        )] for lesson_log in day['lessonLogEntries'] if (value := mark_type.log_value(lesson_log['status']))}

        day_date = datetime.strptime(day['date'], '%Y-%m-%dT%H:%M:%S')
        bells_schedule = get_bells_schedule(day_date)  # TODO: брать из базы данных

        lessons = []
        for lesson in sorted(day['lessons'], key=lambda l: l['number']):
            works = set()
            if lesson_type.classId == ScheduleLesson.classId:
                works = {mark.work for mark in marks.get(lesson['id'], [])}
                for other_marks in others_marks.get(lesson['id'], []):
                    works.update(map(lambda m: m.work, other_marks.marks))
                works.discard(None)  # Удаление None, если есть

            lessons.append(lesson_type(
                number=lesson['number'] - 1,  # Начало с 0
                subject=subjects.get(lesson['subjectId'], "Неизвестный предмет"),
                place=lesson['place'],
                works=list(works),  # Начиная с ScheduleLesson0x0000002C
                hours=ScheduleHours(**bells_schedule[lesson['number'] - 1]),
                logs=marks.get(lesson['id'], []) + logs.get(lesson['id'], []),  # Начиная с ScheduleLesson0x00000017
                othersMarks=others_marks.get(lesson['id'], []),  # Начиная с ScheduleLesson0x00000017
                homework='; '.join(homeworks.get(lesson['id'], [])) or None,
                files=files.get(lesson['id'], [])
            ))

        hours_extracurricular_activities = bells_schedule[len(lessons)] \
            if extracurricular_activities.get(days_hash.get(day['date'])) else None

        result.append(day_type(
            date=day_date.date(),
            lessons=lessons,
            hoursExtracurricularActivities=hours_extracurricular_activities,
            extracurricularActivities=extracurricular_activities.get(days_hash.get(day['date']), []),
        ))

    background_tasks.add_task(log, request, request.url.path, session.session, "200 OK")
    return response_type(
        status=True,
        answer=answer_type(
            schedule=result,
            timezone=session.timezone  # Начиная с ScheduleResult0x00000026
        )
    )


@router.post(
    f"/getMarks/{MarksApiRequest.classId}",
    summary="Получение оценок",
    description="Получение оценок: последних по дате выставления, текущих и итоговых по предметам",
    response_model=MarksApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def _getMarks(request: Request, request_data: MarksApiRequest, background_tasks: BackgroundTasks):
    return await getMarksRequest(request, request_data, background_tasks)


async def getMarksRequest(request: Request, request_data: MarksApiRequest, background_tasks: BackgroundTasks):
    await gather(
        assert_check_api_key(request_data.apiKey),
        assert_check_session(request_data.data.session, check_auth=False)
    )

    session = await get_session(request_data.data.session)
    dnr = AioDnevnikruApi(client=httpx_client, token=session.dnevnik_token)
    now_date = datetime_now(session.timezone).date()
    from_date = now_date - timedelta(days=7)

    try:
        recent_marks, (period_marks, class_rating) = await gather(
            get_recent_marks(session, dnr, background_tasks, from_date=from_date, limit=20),
            get_period_marks(session, dnr, background_tasks)
        )
    except BaseDnevnikruException as e:
        if not await check_auth_session(session.session, dnr, dnevnik_token=session.dnevnik_token, person_id=session.person_id):
            raise SessionError(session=session.session) from e
        raise

    background_tasks.add_task(log, request, request.url.path, session.session, "200 OK")
    return MarksApiResponse(
        answer=MarksResult(
            lastMarks=recent_marks,
            periodMarks=period_marks,
            classRating=class_rating
        )
    )
