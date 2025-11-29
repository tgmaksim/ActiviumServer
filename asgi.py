import json
import codecs
import aiohttp
import traceback

from hashlib import md5
from typing import Optional
from fastapi.responses import JSONResponse
from config import gymnasium_id, no_lessons
from datetime import date, datetime, timedelta, UTC
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Response, Request, HTTPException
from pydnevnikruapi.aiodnevnik import AsyncDiaryAPI, AsyncDiaryError

from core import log, get_bells_schedule
from api import (
    Session,
    get_session,
    auth_session,
    check_session,
    check_api_key,
    create_session,
    get_homeworks_files,
    get_extracurricular_activities,
)


app = FastAPI()


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            print(''.join(traceback.format_exception(e)))
            raise HTTPException(status_code=500, detail="Internal Server Error")


app.add_middleware(ExceptionHandlerMiddleware)


@app.get("/")
async def root(request: Request):
    with codecs.open('./index.html', 'r', encoding='utf-8') as file:
        html: str = file.read()

    await log(request.client.host, request.base_url.path, None, "200 OK")
    return Response(content=html, headers={"Content-Type": "text/html; charset=utf-8"})


@app.post("/login")
async def login(request: Request):
    """
    Обработка запросов /login для создания сессии и последующей авторизации

    Входные параметры:
        apiKey (String): ключ для доступа к API

    Возвращает:
        loginUrl (String): ссылка, по которой нужно перейти, чтобы авторизоваться
        session (String): сгенерированная сессия для дальнейших запросов

    Возможные ошибки:
        400 Bad Request: невалидные JSON-данные; отсутствие обязательных параметров
        403 Forbidden: передан несуществующий apiKey
    """

    try:
        data: dict = await request.json()
        assert await check_api_key(data['apiKey'])

        login_url, session = await create_session()

    except (json.JSONDecodeError, KeyError) as e:
        await log(request.client.host, 'login', None, f"400 Bad Request. {e.__class__.__name__}: {e}")
        raise HTTPException(status_code=400, detail="400 Bad Request")
    except AssertionError:
        await log(request.client.host, 'login', None, "403 Forbidden")
        raise HTTPException(status_code=403, detail="403 Forbidden")

    await log(request.client.host, 'login', None, "200 OK")
    return JSONResponse({'loginUrl': login_url, 'session': session})


@app.get("/authSession/")
async def authSession(request: Request):
    """
    Обработка запросов /authSession для авторизации пользователя.

    После перехода по ссылке для авторизации dnevnik.ru перенаправляет на /authSession и передает
    в hash-параметрах access_token и session. JS перенаправляет на ту же страницу с query-параметрами.
    После получения данных сессия авторизуется и готова к дальнейшим запросам

    Возможные ошибки:
        400 Bad Request: отсутствие обязательных параметров; неудавшаяся аутентификация
        403 Forbidden: API-ошибка, возможно, связанная с неудавшейся аутентификацией; пользователь не состоит в школе
    """

    # Дневник.ру передал access_hash в hash-параметры
    if request.query_params.get('access_token') is None or request.query_params.get('state') is None:
        with codecs.open('./auth_session.html', 'r', encoding='utf-8') as file:
            html: str = file.read()  # Передача параметров из hash в query через JS

        await log(request.client.host, 'authSession', None, "200 OK")

    # JS в браузере передал access_hash в query-параметры
    else:
        token: Optional[str] = request.query_params.get('access_token')
        session: Optional[str] = request.query_params.get('state')
        if token is None or session is None:
            await log(request.client.host, 'authSession', None,
                      f"400 Bad Request. token={token}, state={session}")
            raise HTTPException(status_code=400, detail="400 Bad Request")

        async with aiohttp.ClientSession() as http_client:
            dn = AsyncDiaryAPI(token=token)
            dn.session = http_client

            try:
                person_id = (await dn.get_info())['personId']
                assert (await dn.get_school())[0]['id'] != gymnasium_id

                groups: list[dict] = await dn.get_person_groups(person_id)
                group = filter(lambda g: g['type'] == 'Group', groups).__next__()
                group_id = group['id']

            except (AsyncDiaryError, KeyError, AssertionError, IndexError, StopIteration) as e:
                await log(request.client.host, 'authSession', session,
                          f"403 Forbidden. {e.__class__.__name__}: {e}")
                raise HTTPException(status_code=403, detail="403 Forbidden")

            if not await auth_session(session, token, person_id, group_id):  # Авторизация сессии
                await log(request.client.host, 'authSession', session,
                          f"400 Bad Request. Unsuccessful authentication")
                raise HTTPException(status_code=400, detail="400 Bad Request")

            await log(request.client.host, 'authSession', session, "200 OK")

        with codecs.open('./auth_session.html', 'r', encoding='utf-8') as file:
            html: str = file.read()  # Открытие приложения по ссылке через JS

    return Response(content=html, headers={"Content-Type": "text/html; charset=utf-8"})


@app.post("/checkSession")
async def checkSession(request: Request):
    """
    Проверяет существование сессии и ее авторизация с дневником.ру

    Входные параметры:
        apiKey (String): ключ для доступа к API
        session (String): идентификатор сессии

    Возвращает:
        exists (Boolean): существование сессии
        auth (Boolean): авторизация сессии

    Возможные ошибки:
        400 Bad Request: невалидные JSON-данные; отсутствие обязательных параметров
        403 Forbidden: передан несуществующий apiKey
    """

    try:
        data: dict = await request.json()
        assert await check_api_key(data['apiKey'])

        exists, auth = await check_session(data['session'])

    except (json.JSONDecodeError, KeyError) as e:
        await log(request.client.host, 'checkSession', None,
                  f"400 Bad Request. {e.__class__.__name__}: {e}")
        raise HTTPException(status_code=400, detail="400 Bad Request")
    except AssertionError:
        await log(request.client.host, 'checkSession', None, "403 Forbidden")
        raise HTTPException(status_code=403, detail="403 Forbidden")

    await log(request.client.host, 'checkSession', data['session'], f"exists={exists}, auth={auth}")
    return JSONResponse({'exists': exists, 'auth': auth})


@app.get("/getSchedule")
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
            await log(request.client.host, 'getSchedule', data['session'], "Unauthorized")
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
        await log(request.client.host, 'getSchedule', None,
                  f"400 Bad Request. {e.__class__.__name__}: {e}")
        raise HTTPException(status_code=400, detail="400 Bad Request")
    except AssertionError:
        await log(request.client.host, 'getSchedule', data.get('session'), "403 Forbidden")
        raise HTTPException(status_code=403, detail="403 Forbidden")
    except AsyncDiaryError:
        await log(request.client.host, 'getSchedule', data.get('session'), "APIError")
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
        await log(request.client.host, 'getSchedule', data.get('session'), "APIError")

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
                    await log(request.client.host, 'getSchedule', None, f"{e.__class__.__name__}: {e}")

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
        await log(request.client.host, 'getSchedule', session.session,
                  f"400 Bad Request. {e.__class__.__name__}: {e}")
        result['error'] = True
        return JSONResponse(result)

    await log(request.client.host, 'getSchedule', data.get('session'), "200 OK")
    return JSONResponse(result)
