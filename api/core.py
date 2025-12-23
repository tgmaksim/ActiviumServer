from dataclasses import dataclass
from typing import Optional, Union
from datetime import timedelta, datetime
from asyncpg.exceptions import UniqueViolationError

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from database import Database
from core import log, datetime_now


@dataclass
class Session:
    session: str
    dnevnik_token: str
    person_id: int
    group_id: int


@dataclass
class Cache:
    session: str
    key: str
    value: Union[list, dict]
    datetime: datetime


async def check_api_key(api_key: str) -> bool:
    """Проверка существования API-ключа"""

    sql = "SELECT true FROM api_keys WHERE api_key = $1"
    result = await Database.fetch_row_for_one(sql, api_key)

    return bool(result)


async def check_session(session: str) -> tuple[bool, bool]:
    """Проверка существования сессии и ее авторизации"""

    sql = "SELECT dnevnik_token, person_id, group_id, datetime FROM sessions WHERE session = $1"
    result = await Database.fetch_row(sql, session)

    if not result:
        await log(None, 'checkSession', session, f"Session not found")
        return False, False

    try:
        async with AsyncDiaryAPI(token=result['dnevnik_token']) as dn:
            person_id: int = (await dn.get_info())['personId']
            groups: list[dict] = await dn.get_person_groups(person_id)
            group_id: int = filter(lambda g: g['type'] == 'Group', groups).__next__()['id']  # Класс ученика

    except (AsyncDiaryError, KeyError, StopIteration) as e:
        await log(None, 'checkSession', session, f"{e.__class__.__name__}: {e}")
        return True, False

    authorized = person_id == result['person_id'] and group_id == result['group_id']
    if not authorized:
        await log(None, 'checkSession', session, f"person_id={person_id}, group_id={group_id}")
        return True, False

    if datetime_now() - result['datetime'] > timedelta(days=28):
        await log(None, 'checkSession', session, f"old_session ({result['datetime']})")
        return False, False

    return True, True


async def get_session(session: str) -> Session:
    """Получение сессии из БД"""

    sql = "SELECT session, dnevnik_token, person_id, group_id FROM sessions WHERE session = $1"
    result = await Database.fetch_row(sql, session)

    return Session(
        session=result['session'],
        dnevnik_token=result['dnevnik_token'],
        person_id=result['person_id'],
        group_id=result['group_id']
    )


async def get_cache(session: str, key: str) -> Optional[Cache]:
    """Возвращает значение из кеша (если есть)"""

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
    """Добавление (обновление) значения в кеш по сессии и идентификатору"""

    value = Database.serialize(value)

    try:
        sql = "INSERT INTO cache (session, key, value, datetime) VALUES ($1, $2, $3, NOW())"
        await Database.execute(sql, session, key, value)
    except UniqueViolationError:
        sql = "UPDATE cache SET value = $1, datetime = NOW() WHERE session = $1 AND key = $2"
        await Database.execute(sql, session, key, value)
