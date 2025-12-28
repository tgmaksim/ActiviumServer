from fastapi.requests import Request
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse

from typing import Optional
from aiohttp.abc import URL

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from core import log, templates
from config import server_domain, dnevnik_client_id

from api.core import assert_check_api_key, check_session

from . functions import create_session, auth_session
from . entities import (
    LoginResult,
    LoginApiRequest,
    LoginApiResponse,
    CheckSessionResult,
    CheckSessionApiRequest,
    CheckSessionApiResponse,
)


router = APIRouter(prefix="/login", tags=["Login"])
__all__ = ['router']

# База ссылки для авторизации сессии в сервисе дневник.ру
dnevnik_login_url = URL.build(
    scheme="https",
    host="login.dnevnik.ru",
    path="/oauth2",
    query={
        'response_type': "token",
        'scope': "EducationalInfo",
        'redirect_uri': URL.build(
            scheme="https",
            host=server_domain,
            path="/login/authSession"
        ).__str__(),
        'client_id': dnevnik_client_id,
        'state': ""  # Инициализируется для каждого отдельно
    }
)


@router.post(
    f"/login/{LoginApiRequest.classId}",
    summary="Создание сессии или повторная авторизация",
    description="Метод создает новую сессию и возвращает ее с ссылкой для авторизации. "
                "Если сессия была передана, то в ответе вернется ссылка для ее повторной авторизации (или новая сессия)",
    response_model=LoginApiResponse,
    response_class=JSONResponse,
    status_code=200
)
async def _login(request: Request, request_data: LoginApiRequest):
    await assert_check_api_key(request_data.apiKey)

    session = await create_session(request_data.data.session if request_data.data else None)
    login_url = dnevnik_login_url.update_query(state=session).__str__()

    await log(request, request.url.path, request_data.data.session if request_data.data else None, "200 OK")
    return LoginApiResponse(
        answer=LoginResult(
            loginUrl=login_url,
            session=session
        )
    )


@router.get(
    "/authSession",
    summary="Первичное и вторичное получение параметров от дневника.ру",
    description="После авторизации дневник.ру перенаправит пользователя сюда, "
                "а здесь в свою очередь будет возвращен HTML. "
                "JS возьмет полученные параметры из url#hash и отправит в url?query. \n"
                "Полученные параметры авторизации из url?query от JS используются для последнего этапа авторизации. "
                "Больше этот метод не используется",
    response_class=HTMLResponse,
    status_code=200,
    responses={
        403: {
            'description': "Данный пользователь по определенным причинам не может быть зарегистрирован. "
                           "На данный момент только ученики(цы) Гимназии №147 могут пользоваться приложением",
            'response_description': "Forbidden"
        },
        500: {
            'description': "Произошла ошибка при получении основных данных от дневника.ру. Авторизация прервана",
            'response_description': "Internal Server Error"
        },
        400: {
            'description': "Не удалось авторизовать сессию из-за неверных параметров, например, сессии не существует",
            'response_description': "Bad Request"
        }
    }
)
async def _authSession(request: Request, access_token: Optional[str] = None, state: Optional[str] = None):
    if access_token is None or state is None:
        return templates.TemplateResponse(
            request=request,
            name="auth_session.html"  # Передача параметров из hash в query через JS
        )

    session = state
    token = access_token

    try:
        async with AsyncDiaryAPI(token=token) as dn:
            info: dict = await dn.get_info()
            person_id: int = info['personId']
            timezone: int = int(info['timezone'].split(":")[0])
            gymnasium_id: int = (await dn.get_school())[0]['id']

            groups: list[dict] = await dn.get_person_groups(person_id)
            group_id: int = filter(lambda g: g['type'] == 'Group', groups).__next__()['id']  # Класс

    except (AsyncDiaryError, KeyError, IndexError, StopIteration) as e:
        await log(request, request.url.path, session, f"{e.__class__.__name__}: {e}")
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            status_code=500,
            context={
                'summary': "Произошла ошибка авторизации",
                'description': "Произошла ошибка при получении основных данных от дневника.ру. Авторизация прервана"
            }
        )

    if not await auth_session(session, token, person_id, group_id, gymnasium_id, timezone):  # Авторизация сессии
        await log(request, request.url.path, session, f"400 Bad Request. Unsuccessful authentication")
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            status_code=400,
            context={
                'summary': "Произошла ошибка авторизации",
                'description': "Дневник.ру вернул некорректные данные, попробуйте еще раз"
            }
        )

    await log(request, request.url.path, session, "200 OK")

    response = templates.TemplateResponse(
        request=request,
        name="auth_session.html"
    )
    response.set_cookie(
        key="session",
        value=session,
        max_age=30 * 24 * 60 * 60,  # 30 дней
        httponly=True,
        secure=True
    )
    return response


@router.post(
    f"/checkSession/{CheckSessionApiRequest.classId}",
    summary="Проверка сессии",
    description="Проверка сессии на существование и авторизацию. "
                "Не рекомендуется использовать, так как любые методы проверяют сессию самостоятельно",
    response_model=CheckSessionApiResponse,
    response_class=JSONResponse,
    status_code=200,
    deprecated=True
)
async def _checkSession(request: Request, request_data: CheckSessionApiRequest):
    await assert_check_api_key(request_data.apiKey)

    session = request_data.data.session
    exists, auth = await check_session(session, check_auth=True)

    await log(request, request.url.path, session, f"exists={exists}, auth={auth}")
    return CheckSessionApiResponse(
        answer=CheckSessionResult(
            exists=exists,
            auth=auth
        )
    )
