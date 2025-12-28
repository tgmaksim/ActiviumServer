from dataclasses import dataclass
from typing import Optional, Union
from datetime import timedelta, datetime
from asyncpg.exceptions import UniqueViolationError

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from database import Database
from core import log, datetime_now


SESSION_LIFETIME = 28  # Время жизни сессии в днях


class ApiKeyError(Exception):
    """API-ключ не существует"""

    def __init__(self, *, api_key: str):
        self.api_key = api_key


class SessionError(Exception):
    """Сессия не существует или не авторизована"""

    def __init__(self, *, session: str):
        self.session = session


@dataclass
class Session:
    """Данные сессии пользователя"""

    session: str  # Строковый идентификатор сессии
    dnevnik_token: str  # Токен для взаимодействия с аккаунтом дневника.ру
    person_id: int  # Идентификатор person в дневнике.ру
    group_id: int  # Идентификатор класса ученика(цы) в дневнике.ру
    gymnasium_id: int  # Идентификатор школы ученика(цы) в дневнике.ру
    timezone: int  # Часовой пояс


@dataclass
class Cache:
    """Кешированные данные в БД"""

    session: str  # Строковый идентификатор сессии, к которой привязан кеш
    key: str  # Ключ (идентификатор) кеша для пользователя
    value: Union[list, dict]  # Значение кеша в формате JSON
    datetime: datetime  # Дата и время заполнения данных


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
        if not await check_auth_session(session, dnevnik_token=result['dnevnik_token'], person_id=result['person_id']):
            return True, False

    if datetime_now() - result['datetime'] > timedelta(days=SESSION_LIFETIME):
        await log(None, 'checkSession', session, f"old_session ({result['datetime']})")
        return False, False

    return True, True


async def check_auth_session(session: str, *, dnevnik_token: Optional[str] = None, person_id: Optional[int] = None) -> bool:
    """
    Проверка авторизации сессии

    :param session: строковый идентификатор сессии
    :param dnevnik_token: токен для взаимодействия с аккаунтом дневника.ру
    :param person_id: идентификатор ученика(цы)
    :return: авторизация сессии
    """

    if not dnevnik_token or not person_id:
        sql = "SELECT dnevnik_token, person_id FROM sessions WHERE session = $1"
        result = await Database.fetch_row(sql, session)

        dnevnik_token, person_id = result['dnevnik_token'], result['person_id']

    try:
        async with AsyncDiaryAPI(token=dnevnik_token) as dn:
            _person_id: int = (await dn.get_info())['personId']

    except (AsyncDiaryError, KeyError) as e:
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


async def get_cache(session: str, key: str) -> Optional[Cache]:
    """
    Получение значение из кеша в базе данных по сессии и ключу

    :param session: строковый идентификатор сессии
    :param key: ключ к значению данных в кеше
    :return: данные кеша, если найдены
    """

    sql = "SELECT value, datetime FROM cache WHERE session = $1 AND key = $2"
    result = await Database.fetch_row(sql, session, key)

    if not result:
        return None

    if datetime_now() - result['datetime'] > timedelta(days=1):
        sql = "DELETE FROM cache WHERE session = $1 AND key = $2"
        await Database.execute(sql, session, key)
        return None

    return Cache(
        session=session,
        key=key,
        value=result['value'],
        datetime=result['datetime']
    )


async def put_cache(session: str, key: str, value: Union[list, dict]):
    """
    Добавление (обновление) значения в кеше по сессии и ключу

    :param session: строковый идентификатор сессии
    :param key: ключ к значению в кеше
    :param value: значение, которое нужно положить в кеш по ключу
    """

    value = Database.serialize(value)  # Сериализация в строковый формат JSON

    try:
        sql = "INSERT INTO cache (session, key, value, datetime) VALUES ($1, $2, $3, NOW())"
        await Database.execute(sql, session, key, value)
    except UniqueViolationError:
        sql = "UPDATE cache SET value = $3, datetime = NOW() WHERE session = $1 AND key = $2"
        await Database.execute(sql, session, key, value)
