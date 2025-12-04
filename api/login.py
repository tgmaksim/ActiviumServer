import json
import codecs
import aiohttp

from typing import Optional
from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, Response
from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from core import log
from config import gymnasium_id, server_domain, dnevnik_client_id
from .core import (
    auth_session,
    check_api_key,
    check_session,
    create_session,
)


router = APIRouter(prefix="/v1/login")
dnevnik_login_url = ("https://login.dnevnik.ru/oauth2?"
                     "response_type=token&"
                     "scope=EducationalInfo&"
                     f"redirect_uri=https://{server_domain}/v1/login/authSession&"
                     f"client_id={dnevnik_client_id}")


@router.post("/login")
async def login(request: Request):
    """
    Обработка запросов /login для создания сессии и последующей авторизации

    Входные параметры:
        apiKey (String): ключ для доступа к API
        session (String) optional: предыдущая сессия, если нужно сохранить

    Возвращает:
        loginUrl (String): ссылка, по которой нужно перейти, чтобы авторизоваться
        session (String): сгенерированная сессия для дальнейших запросов или входящая

    Возможные ошибки:
        400 Bad Request: невалидные JSON-данные; отсутствие обязательных параметров
        403 Forbidden: передан несуществующий apiKey
    """

    try:
        data: dict = await request.json()
        assert await check_api_key(data['apiKey'])

        session = await create_session(data.get('session'))
        login_url = f"{dnevnik_login_url}&state={session}"

    except (json.JSONDecodeError, KeyError) as e:
        await log(request, 'login', None, f"400 Bad Request. {e.__class__.__name__}: {e}")
        raise HTTPException(status_code=400, detail="400 Bad Request")
    except AssertionError:
        await log(request, 'login', None, "403 Forbidden")
        raise HTTPException(status_code=403, detail="403 Forbidden")

    await log(request, 'login', None, "200 OK")
    return JSONResponse({'loginUrl': login_url, 'session': session})


@router.get("/authSession")
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

        await log(request, 'authSession', None, "200 OK")

    # JS в браузере передал access_hash в query-параметры
    else:
        token: Optional[str] = request.query_params.get('access_token')
        session: Optional[str] = request.query_params.get('state')
        if token is None or session is None:
            await log(request, 'authSession', None,
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
                await log(request, 'authSession', session,
                          f"403 Forbidden. {e.__class__.__name__}: {e}")
                raise HTTPException(status_code=403, detail="403 Forbidden")

            if not await auth_session(session, token, person_id, group_id):  # Авторизация сессии
                await log(request, 'authSession', session,
                          f"400 Bad Request. Unsuccessful authentication")
                raise HTTPException(status_code=400, detail="400 Bad Request")

            await log(request, 'authSession', session, "200 OK")

        with codecs.open('./auth_session.html', 'r', encoding='utf-8') as file:
            html: str = file.read()  # Открытие приложения по ссылке через JS

    return Response(content=html, headers={"Content-Type": "text/html; charset=utf-8"})


@router.post("/checkSession")
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
        await log(request, 'checkSession', None,
                  f"400 Bad Request. {e.__class__.__name__}: {e}")
        raise HTTPException(status_code=400, detail="400 Bad Request")
    except AssertionError:
        await log(request, 'checkSession', None, "403 Forbidden")
        raise HTTPException(status_code=403, detail="403 Forbidden")

    await log(request, 'checkSession', data['session'], f"exists={exists}, auth={auth}")
    return JSONResponse({'exists': exists, 'auth': auth})
