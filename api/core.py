from datetime import timedelta, datetime as _datetime
from typing import Optional, Union
from pydantic import BaseModel, Field

from dnevnikru import AioDnevnikruApi, BaseDnevnikruException

from database import Database
from core import log, datetime_now, httpx_client


__all__ = ['SESSION_LIFETIME', 'ApiKeyError', 'SessionError', 'Session', 'Cache', 'assert_check_api_key',
           'check_session', 'check_auth_session', 'assert_check_session', 'get_session', 'get_cache', 'get_caches',
           'put_caches', 'put_cache']

SESSION_LIFETIME = 28  # Время жизни сессии в днях


class ApiKeyError(Exception):
    """API-ключ не существует"""

    def __init__(self, *, api_key: str):
        self.api_key = api_key


class SessionError(Exception):
    """Сессия не существует или не авторизована"""

    def __init__(self, *, session: str):
        self.session = session


class Session(BaseModel):
    """Данные сессии пользователя"""

    session: str = Field(
        description="Строковый идентификатор сессии"
    )
    dnevnik_token: str = Field(
        description="Токен для взаимодействия с аккаунтом дневника.ру"
    )
    person_id: int = Field(
        description="Идентификатор person в дневнике.ру"
    )
    group_id: int = Field(
        description="Идентификатор класса обучающегося в дневнике.ру"
    )
    gymnasium_id: int = Field(
        description="Идентификатор школы обучающегося в дневнике.ру"
    )
    timezone: int = Field(
        description="Часовой пояс"
    )


class Cache(BaseModel):
    """Кешированные данные в БД"""

    session: str = Field(
        description="Строковый идентификатор сессии, к которой привязан кеш"
    )
    key: str = Field(
        description="Ключ (идентификатор) кеша для пользователя"
    )
    value: Union[list, dict] = Field(
        description="Значение кеша в формате JSON"
    )
    datetime: _datetime = Field(
        description="Дата и время заполнения данных"
    )


async def assert_check_api_key(api_key: str):
    """
    Проверка существования API-ключа и выбрасывание исключения, если API-ключ не существует

    :param api_key: строковый API-ключ для проверки
    :except ApiKeyError: API-ключ не существует
    """

    sql = "SELECT true FROM api_keys WHERE api_key = $1"
    result = await Database.fetch_row_for_one(sql, api_key)

    if result is not True:
        raise ApiKeyError(api_key=api_key)


async def check_session(session: str, *, check_auth: bool) -> tuple[bool, bool]:
    """
    Проверка существования сессии и ее авторизации

    :param session: строковый идентификатор сессии
    :param check_auth: необходимость проверить авторизацию сессии
    :return: существование сессии, авторизация сессии (если существует)
    """

    sql = "SELECT dnevnik_token, person_id, datetime FROM sessions WHERE session = $1"
    result = await Database.fetch_row(sql, session)

    if not result:
        await log(None, 'checkSession', session, f"Session not found")
        return False, False

    if check_auth:
        dnr = AioDnevnikruApi(client=httpx_client, token=result['dnevnik_token'])
        if not await check_auth_session(session, dnr, dnevnik_token=result['dnevnik_token'], person_id=result['person_id']):
            return True, False

    if datetime_now() - result['datetime'] > timedelta(days=SESSION_LIFETIME):
        await log(None, 'checkSession', session, f"old_session ({result['datetime']})")
        return False, False

    return True, True


async def check_auth_session(
        session: str,
        dnr: AioDnevnikruApi,
        *,
        dnevnik_token: Optional[str] = None,
        person_id: Optional[int] = None
) -> bool:
    """
    Проверка авторизации сессии

    :param session: строковый идентификатор сессии
    :param dnr: объект AioDnevnikruApi для совершения запросов
    :param dnevnik_token: токен для взаимодействия с аккаунтом дневника.ру
    :param person_id: идентификатор ученика(цы)
    :return: авторизация сессии
    """

    if not dnevnik_token or not person_id:
        sql = "SELECT dnevnik_token, person_id FROM sessions WHERE session = $1"
        result = await Database.fetch_row(sql, session)

        dnevnik_token, person_id = result['dnevnik_token'], result['person_id']

    try:
        _person_id: int = (await dnr.get_info())['personId']
    except (BaseDnevnikruException, KeyError) as e:
        await log(None, 'checkAuthSession', session, f"{e.__class__.__name__}: {e}")
        return False

    authorized = person_id == _person_id
    if not authorized:
        await log(None, 'checkAuthSession', session, f"person_id={person_id}")
        return False

    return True


async def assert_check_session(session: str, *, check_auth: bool):
    """
    Проверка существования сессии и ее авторизации и выбрасывание исключения, если API-ключ не существует

    :param session: строковый идентификатор сессии
    :param check_auth: необходимость проверить авторизацию сессии
    :except SessionError: сессия не существует или не авторизована
    """

    if not all(await check_session(session, check_auth=check_auth)):
        raise SessionError(session=session)


async def get_session(session: str) -> Session:
    """
    Получение данных сессий по строковому идентификатору

    :param session: строковый идентификатор сессии
    :return: данные сессии
    """

    sql = "SELECT session, dnevnik_token, person_id, group_id, gymnasium_id, timezone FROM sessions WHERE session = $1"
    result = await Database.fetch_row(sql, session)

    return Session(
        session=result['session'],
        dnevnik_token=result['dnevnik_token'],
        person_id=result['person_id'],
        group_id=result['group_id'],
        gymnasium_id=result['gymnasium_id'],
        timezone=result['timezone']
    )


async def get_caches(session: str, keys: list[str]) -> dict[str, Cache]:
    """
    Получение значение из кеша в базе данных по сессии и ключу

    :param session: строковый идентификатор сессии
    :param keys: ключи к значению данных в кеше
    :return: данные кеша, если найдены, по ключу
    """

    sql = "SELECT key, value, datetime FROM cache WHERE session = $1 AND key = ANY($2::text[])"
    results = await Database.fetch_all(sql, session, keys)

    return {result['key']: Cache(
        session=session,
        key=result['key'],
        value=result['value'],
        datetime=result['datetime']
    ) for result in results}


async def get_cache(session: str, key: str) -> Optional[Cache]:
    """
    Получение значение из кеша в базе данных по сессии и ключу

    :param session: строковый идентификатор сессии
    :param key: ключ к значению данных в кеше
    :return: данные кеша, если найдены
    """

    return (await get_caches(session, [key])).get(key)


async def put_caches(session: str, keys: list[str], values: list[Union[list, dict]]):
    """
    Добавление (обновление) значений в кеше по сессии и ключам

    :param session: строковый идентификатор сессии
    :param keys: ключи к значениям в кеше
    :param values: значения, которые нужно положить в кеш по ключам
    """

    params = [(session, keys[i], Database.serialize(values[i])) for i in range(len(keys))]

    sql = """
            INSERT INTO cache (session, key, value, datetime)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (session, key)
            DO UPDATE SET
                value = EXCLUDED.value,
                datetime = EXCLUDED.datetime
          """

    await Database.executemany(sql, params)


async def put_cache(session: str, key: str, value: Union[list, dict]):
    """
    Добавление (обновление) значения в кеше по сессии и ключу

    :param session: строковый идентификатор сессии
    :param key: ключ к значению в кеше
    :param value: значение, которое нужно положить в кеш по ключу
    """

    return await put_caches(session, [key], [value])
