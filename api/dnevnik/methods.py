from hashlib import md5
from datetime import datetime, timedelta, UTC
from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from api.entities import ApiError
from core import log, get_bells_schedule
from api.core import check_api_key, check_session, get_session

from . functions import get_homeworks_files, get_extracurricular_activities
from . entities import ScheduleApiRequest, ScheduleApiResponse, ScheduleLesson, ScheduleDay, ScheduleResult, ScheduleHours


router = APIRouter(prefix=f"/dnevnik", tags=["Dnevnik"])
__all__ = ['router']


@router.post(
    f"/getSchedule/{ScheduleApiRequest.classId}",
    summary="Получение расписания",
    description="Получение расписания на 2 недели (15 дней) с домашними заданиями, внеурочками и другими данными",
    response_model=ScheduleApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def getSchedule(request: Request, request_data: ScheduleApiRequest):
    if not await check_api_key(request_data.apiKey):
        return ScheduleApiResponse(
            status=False,
            error=ApiError(
                type="InvalidApiKey",
                errorMessage="Приложение повреждено или скачано из неофициального источника. Обратитесь в поддержку"
            )
        )

    try:
        if not all(await check_session(request_data.data.session)):
            await log(request, 'getSchedule', request_data.data.session, "Unauthorized")
            return ScheduleApiResponse(
                status=False,
                error=ApiError(
                    type="Unauthorized",
                    errorMessage="Требуется повторная авторизация"
                )
            )

        session = await get_session(request_data.data.session)

        async with AsyncDiaryAPI(token=session.dnevnik_token) as dn:
            # Период 2 недели (15 дней) с учетом часового пояса (+06:00)
            start_date = (datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=6)).date()
            end_date = (datetime.now(UTC).replace(tzinfo=None) + timedelta(days=14, hours=6)).date()

            # Расписание конкретно для пользователя
            schedule = await dn.get_person_schedule(
                session.person_id,
                session.group_id,
                str(start_date),
                str(end_date)
            )

    except AsyncDiaryError:
        await log(request, 'getSchedule', request_data.data.session, "ApiError")
        return ScheduleApiResponse(
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
                str(start_date),
                str(end_date)
            )

    except AsyncDiaryError:
        await log(request, 'getSchedule', request_data.data.session, "APIError")

    result = []
    for day in schedule['days']:
        lessons: list[ScheduleLesson] = []

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
                await log(request, 'getSchedule', None, f"{e.__class__.__name__}: {e}")
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

            lessons.append(ScheduleLesson(
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

        # Используя полученный md5, можно получить внеурочки класса
        extracurricular_activities = await get_extracurricular_activities(
            session.group_id, day_date.weekday(), day_hash)
        hours_extracurricular_activities = bells_schedule[len(lessons)] if extracurricular_activities else None

        result.append(ScheduleDay(
            date=day_date.date().strftime('%Y-%m-%d'),
            lessons=lessons,
            hoursExtracurricularActivities=hours_extracurricular_activities,
            extracurricularActivities=extracurricular_activities
        ))

    await log(request, 'getSchedule', request_data.data.session, "200 OK")
    return ScheduleApiResponse(
        status=True,
        answer=ScheduleResult(
            schedule=result
        )
    )
