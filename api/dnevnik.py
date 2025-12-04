import json
import aiohttp

from hashlib import md5
from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta, date, UTC
from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from config import no_lessons
from core import log, get_bells_schedule
from .core import (
    check_api_key,
    check_session,
    get_session,
    Session,
    get_homeworks_files,
    get_extracurricular_activities,
)


router = APIRouter(prefix="/v1/dnevnik")


@router.get("/getSchedule")
async def getSchedule(request: Request):
    """
    Отдает расписание пользователя на две недели (15 дней)

    Входные параметры:
        apiKey (String): ключ для доступа к API
        session (String): идентификатор сессии

    Возвращает:
        status (Boolean): статус запроса
        unauthorized (Boolean): сессия требует авторизации
        error (Boolean): возникла внутренняя ошибка
        schedules (Array, JSON): расписание на 2 недели (15 дней) - список дней
            date (String): дата дня в формате YYYY-MM-DD
            lessons (Array, JSON): список уроков в этот день
                number (Integer): номер урока в порядке провождения
                subject (String): название предмета
                place (String): кабинет
                hours (String): время урока в формате HH:MM - HH:MM
                homework (String): домашнее задание
            hoursExtracurricularActivities (Integer/null): время проведения внеурочки
            extracurricularActivities (Array, JSON): внеурочки у класса в этот день (проводятся одновременно)
                subject (String): название предмета
                place (String): кабинет

    Возможные ошибки:
        400 Bad Request: невалидные JSON-данные; отсутствие обязательных параметров
        403 Forbidden: передан несуществующий apiKey
    """

    result = {
        'status': False,
        'unauthorized': False,
        'error': False,
        'schedule': [],
    }

    data: dict = {}
    try:
        data = await request.json()
        assert await check_api_key(data['apiKey'])

        if not all(await check_session(data['session'])):
            await log(request, 'getSchedule', data['session'], "Unauthorized")
            result['unauthorized'] = True
            return JSONResponse(result)

        session: Session = await get_session(data['session'])
        async with aiohttp.ClientSession() as http_client:
            dn = AsyncDiaryAPI(token=session.dnevnik_token)
            dn.session = http_client

            # Период 2 недели (15 дней) с учетом часового пояса
            start_date = date.today()
            end_date = (datetime.now(UTC).replace(tzinfo=None) + timedelta(days=14, hours=6)).date()

            # Расписание конкретно для пользователя
            schedule = await dn.get_person_schedule(
                session.person_id,
                session.group_id,
                str(start_date),
                str(end_date)
            )

    except (json.JSONDecodeError, KeyError) as e:
        await log(request, 'getSchedule', None,
                  f"400 Bad Request. {e.__class__.__name__}: {e}")
        raise HTTPException(status_code=400, detail="400 Bad Request")
    except AssertionError:
        await log(request, 'getSchedule', data.get('session'), "403 Forbidden")
        raise HTTPException(status_code=403, detail="403 Forbidden")
    except AsyncDiaryError:
        await log(request, 'getSchedule', data.get('session'), "APIError")
        result['error'] = True
        return JSONResponse(result)

    all_schedule = []
    try:
        async with aiohttp.ClientSession() as http_client:
            dn = AsyncDiaryAPI(token=session.dnevnik_token)
            dn.session = http_client

            # Полное расписание всего класса (в том числе других профилей и подгрупп)
            all_schedule = await dn.get_group_lessons_info(
                session.group_id,
                str(start_date),
                str(end_date)
            )

    except AsyncDiaryError:
        await log(request, 'getSchedule', data.get('session'), "APIError")

    result['status'] = True
    try:
        for day in schedule['days']:
            lessons = []
            subjects = {}

            day_date = datetime.strptime(day['date'], '%Y-%m-%dT%H:%M:%S')
            bells_schedule = get_bells_schedule(day_date)

            for lesson in sorted(day['lessons'], key=lambda l: l['number']):
                if lesson['subjectId'] in no_lessons:
                    continue  # Классные часы не входят в расписание уроков

                if lesson['subjectId'] in subjects.values():
                    subjects[lesson['id']] = lesson['subjectId']
                    continue  # Считается не каждый урок, а весь блок
                subjects[lesson['id']] = lesson['subjectId']

                # Классный час первым уроков в эти дни
                first_class_hour = day_date.weekday() in (0, 3)

                files = {}
                try:
                    homework_ids = list(map(lambda h: h['id'],
                                            filter(lambda h: h['subjectId'] == subjects[lesson['id']] and h['files'],
                                                   day['homeworks'])))
                    files = await get_homeworks_files(session.dnevnik_token, homework_ids)
                except AsyncDiaryError as e:
                    await log(request, 'getSchedule', None, f"{e.__class__.__name__}: {e}")

                lessons.append({
                    'number': (lesson['number'] - 1 - first_class_hour) // 2,
                    'subject': filter(lambda s: s['id'] == lesson['subjectId'],
                                      day['subjects']).__next__()['name'],
                    'place': lesson['place'],
                    'hours': bells_schedule[(lesson['number'] - 1 - first_class_hour) // 2],
                    'homework': '\n'.join(list(
                        map(lambda h: h['text'],
                            filter(lambda h: h['subjectId'] == subjects[lesson['id']],
                                   day['homeworks'])))),
                    'files': files
                })

            # Получаем md5-хеш расписания на день:
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
                ).encode('utf-8')).hexdigest()

            # Получаем внеурочки класса
            extracurricular_activities = await get_extracurricular_activities(
                session.group_id, day_date.weekday(), day_hash)
            hours_extracurricular_activities = bells_schedule[len(lessons)] if extracurricular_activities else None
            for i in extracurricular_activities:
                i['place'] = str(i['place'])

            result['schedule'].append({
                'date': day_date.date().strftime('%Y-%m-%d'),
                'lessons': lessons,
                'hoursExtracurricularActivities': hours_extracurricular_activities,
                'extracurricularActivities': extracurricular_activities
            })

    except (KeyError, StopIteration) as e:
        await log(request, 'getSchedule', session.session,
                  f"400 Bad Request. {e.__class__.__name__}: {e}")
        result['error'] = True
        return JSONResponse(result)

    await log(request, 'getSchedule', data.get('session'), "200 OK")
    return JSONResponse(result)
