import aiohttp
import asyncpg

from core import log
from hashlib import sha256
from datetime import datetime
from database import Database
from dataclasses import dataclass
from config import dnevnik_login_url
from pydnevnikruapi.aiodnevnik import AsyncDiaryAPI, AsyncDiaryError


@dataclass
class Session:
    session: str
    dnevnik_token: str
    person_id: int
    group_id: int


async def check_api_key(api_key: str) -> bool:
    """Проверяет существование API-ключа"""

    sql = "SELECT app_name FROM api_keys WHERE api_key = $1"
    result = await Database.fetch_row_for_one(sql, api_key)

    return bool(result)


async def create_session() -> tuple[str, str]:
    """Создает новую сессию и возвращает url для связи сессии с дневником.ру и идентификатор сессии"""

    session = sha256(str(datetime.now()).encode('utf-8')).hexdigest()

    sql = "INSERT INTO sessions (session, dnevnik_token, person_id, group_id) VALUES ($1, NULL, NULL, NULL)"
    await Database.execute(sql, session)

    return f"{dnevnik_login_url}&state={session}", session


async def auth_session(session: str, token: str, person_id: int, group_id: int) -> bool:
    """Авторизует сессию и возвращает результат"""

    sql = "SELECT session FROM sessions WHERE session = $1"
    result = await Database.fetch_row_for_one(sql, session)
    if not result:
        return False  # Сессия не существует

    try:
        sql = "UPDATE sessions SET dnevnik_token = $1, person_id = $2, group_id = $3 WHERE session = $4"
        await Database.execute(sql, token, person_id, group_id, session)

    except asyncpg.exceptions.StringDataRightTruncationError:
        return False  # Переполнение длины dnevnik_token

    return True


async def check_session(session: str) -> tuple[bool, bool]:
    """Проверяет существование сессии ее аутентификация"""

    sql = "SELECT dnevnik_token, person_id, group_id FROM sessions WHERE session = $1"
    result = await Database.fetch_row(sql, session)

    if not result:
        await log(None, 'scheckSession', session, "Session not found")
        return False, False

    try:
        async with aiohttp.ClientSession() as http_client:
            dn = AsyncDiaryAPI(token=result['dnevnik_token'])
            dn.session = http_client

            person_id = (await dn.get_info()).get('personId')
            groups = (await dn.get_person_groups(person_id))
            group_id = filter(lambda g: g['type'] == 'Group', groups).__next__()['id']

    except (AsyncDiaryError, IndexError) as e:
        await log(None, 'scheckSession', session, f"{e.__class__.__name__}: {e}")
        return True, False

    authorized = person_id  == result['person_id'] and group_id == result['group_id']
    if not authorized:
        await log(None, 'scheckSession', session, f"person_id={person_id}, group_id={group_id}")
    return True, authorized


async def get_session(session: str) -> Session:
    """Получает сессию из БД"""

    sql = "SELECT session, dnevnik_token, person_id, group_id FROM sessions WHERE session = $1"
    result = await Database.fetch_row(sql, session)

    return Session(
        session=result['session'],
        dnevnik_token=result['dnevnik_token'],
        person_id=result['person_id'],
        group_id=result['group_id']
    )


# В оригинальном методе баг
async def get_person_schedule(
    self: AsyncDiaryAPI,
    person_id,
    group_id,
    start_time: str = str(datetime.now()),
    end_time: str = str(datetime.now()),
):
    person_schedule = await self.get(
        f"persons/{person_id}/groups/{group_id}/schedules",
        params={"startDate": start_time, "endDate": end_time},
    )
    return person_schedule


AsyncDiaryAPI.get_person_schedule = get_person_schedule
