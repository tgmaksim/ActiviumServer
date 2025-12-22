from hashlib import md5
from typing import Union
from datetime import timedelta, datetime

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from core import log, get_bells_schedule, datetime_now

from api.entities import ApiError
from api.core import check_api_key, check_session, get_session

from . functions import get_homeworks_files, get_extracurricular_activities
from . entities import (
    ScheduleLog,
    ScheduleDay,
    ScheduleHours,
    ScheduleResult,
    ScheduleLesson,
    ScheduleApiRequest,
    ScheduleApiResponse,
    ScheduleDay0x00000012,
    ScheduleLesson0x00000011,
    ScheduleResult0x00000013,
    ScheduleApiRequest0x0000000D,
    ScheduleApiResponse0x00000014,
)


router = APIRouter(prefix=f"/dnevnik", tags=["Dnevnik"])
__all__ = ['router']


@router.post(
    f"/getSchedule/{ScheduleApiRequest0x0000000D.classId}",
    summary="Получение расписания",
    description="Получение расписания на 2 недели (15 дней) с домашними заданиями и внеурочными занятиями"
                f"Устаревший метод в пользу {ScheduleApiRequest.classId}",
    response_model=ScheduleApiResponse0x00000014,
    response_class=JSONResponse,
    status_code=200,
    deprecated=True,
)
async def _getSchedule(request: Request, request_data: ScheduleApiRequest0x0000000D):
    return await getScheduleRequest(request, request_data)


@router.post(
    f"/getSchedule/{ScheduleApiRequest.classId}",
    summary="Получение расписания",
    description="Получение расписания на 2 недели (15 дней) с домашними заданиями, внеурочными занятиями и "
                "оценками с отметками посещаемости за сегодняшний день",
    response_model=ScheduleApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def _getSchedule(request: Request, request_data: ScheduleApiRequest):
    return await getScheduleRequest(request, request_data)


async def getScheduleRequest(request: Request, request_data: Union[ScheduleApiRequest0x0000000D, ScheduleApiRequest]):
    response_type = ScheduleApiResponse if request_data.classId == ScheduleApiRequest.classId \
        else ScheduleApiResponse0x00000014
    day_type = ScheduleDay if request_data.classId == ScheduleApiRequest.classId \
        else ScheduleDay0x00000012
    answer_type = ScheduleResult if request_data.classId == ScheduleApiRequest.classId \
        else ScheduleResult0x00000013

    now_date = datetime_now(6).date()

    if not await check_api_key(request_data.apiKey):
        return response_type(
            status=False,
            error=ApiError(
                type="InvalidApiKeyError",
                errorMessage="Приложение повреждено или скачано из неофициального источника. Обратитесь в поддержку"
            )
        )

    try:
        if not all(await check_session(request_data.data.session)):
            await log(request, request.url.path, request_data.data.session, "Unauthorized")
            return response_type(
                status=False,
                error=ApiError(
                    type="UnauthorizedError",
                    errorMessage="Требуется повторная авторизация"
                )
            )

        session = await get_session(request_data.data.session)

        # Период 2 недели (15 дней) с учетом часового пояса (+06:00)
        end_date = (datetime_now(6) + timedelta(days=14)).date()

        async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
            # Расписание конкретно для пользователя
            schedule = await dn.get_person_schedule(
                session.person_id,
                session.group_id,
                str(now_date),
                str(end_date)
            )

    except AsyncDiaryError:
        await log(request, request.url.path, request_data.data.session, "ApiError")
        return response_type(
            status=False,
            error=ApiError(
                type="InternalServerError"
            )
        )

    all_schedule = []
    try:
        async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
            # Полное расписание всего класса (в том числе других профилей и подгрупп)
            all_schedule = await dn.get_group_lessons_info(
                session.group_id,
                str(now_date),
                str(end_date)
            )

    except AsyncDiaryError:
        await log(request, request.url.path, request_data.data.session, "APIError")

    logs = {}

    if request_data.classId == ScheduleApiRequest.classId:
        try:
            async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
                marks = await dn.get(f"persons/{session.person_id}/edu-groups/{session.group_id}/marks/{now_date}/{now_date}")

            for mark in marks:
                if logs.get(mark['lesson']) is None:
                    logs[mark['lesson']] = []

                logs[mark['lesson']].append(ScheduleLog(
                    mood=mark['mood'].lower() if mark['mood'].lower() in ScheduleLog.moods() else ScheduleLog.default_mood(),
                    value=mark['value']
                ))

        except AsyncDiaryError:
            await log(request, request.url.path, request_data.data.session, "APIError")
            return response_type(
                status=False,
                error=ApiError(
                    type="InternalServerError"
                )
            )

        try:
            async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
                lesson_logs = (await dn.get_person_lesson_logs(session.person_id, str(now_date), str(now_date)))['logEntries']

            for lesson_log in lesson_logs:
                if logs.get(lesson_log['lesson']) is None:
                    logs[lesson_log['lesson']] = []

                if value := ScheduleLog.log_value(lesson_log['status']):
                    logs[lesson_log['lesson']].append(ScheduleLog(
                        mood=ScheduleLog.default_mood(),
                        value=value
                    ))

        except (AsyncDiaryError, KeyError) as e:
            await log(request, request.url.path, request_data.data.session, f"{e.__class__.__name__}: {e}")
            return response_type(
                status=False,
                error=ApiError(
                    type="InternalServerError"
                )
            )

    result = []
    for day in schedule['days']:
        lessons = []

        day_date = datetime.strptime(day['date'], '%Y-%m-%dT%H:%M:%S')
        bells_schedule = get_bells_schedule(day_date)

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

            if request_data.classId == ScheduleApiRequest.classId:
                lessons.append(ScheduleLesson(
                    number=lesson['number'] - 1,
                    subject=subject,
                    place=lesson['place'],
                    hours=ScheduleHours(**bells_schedule[lesson['number'] - 1]),
                    logs=logs.get(lesson['id'], []),
                    othersMarks=[],  # Пока что заглушка TODO: добавить данные
                    homework=homework or None,
                    files=files
                ))
            else:
                lessons.append(ScheduleLesson0x00000011(
                    number=lesson['number'] - 1,
                    subject=subject,
                    place=lesson['place'],
                    hours=ScheduleHours(**bells_schedule[lesson['number'] - 1]),
                    homework=homework or None,
                    files=files
                ))

        # Получение md5-хеша расписания на день:
        # сортированный список из id предметов всего класса на данный день
        day_hash = md5(
            str(
                sorted(
                    map(
                        lambda l: l['subject']['id'],
                        filter(
                            lambda l: l['date'] == day['date'],
                            all_schedule
                        )
                    )
                )
            ).encode('utf-8')
        ).hexdigest()

        # Используя полученный md5, можно получить внеурочные занятия класса
        extracurricular_activities = await get_extracurricular_activities(
            session.group_id, day_date.weekday(), day_hash)
        hours_extracurricular_activities = bells_schedule[len(lessons)] if extracurricular_activities else None

        result.append(day_type(
            date=day_date.date().strftime('%Y-%m-%d'),
            lessons=lessons,
            hoursExtracurricularActivities=hours_extracurricular_activities,
            extracurricularActivities=extracurricular_activities
        ))

    await log(request, request.url.path, request_data.data.session, "200 OK")
    return response_type(
        status=True,
        answer=answer_type(
            schedule=result
        )
    )
