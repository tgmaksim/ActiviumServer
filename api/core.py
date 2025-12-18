from dataclasses import dataclass

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI
from pydnevnikruapi.aiodnevnik.exceptions import AsyncDiaryError

from core import log
from database import Database


@dataclass
class Session:
    session: str
    dnevnik_token: str
    person_id: int
    group_id: int


async def check_api_key(api_key: str) -> bool:
    """Проверка существования API-ключа"""

    sql = "SELECT true FROM api_keys WHERE api_key = $1"
    result = await Database.fetch_row_for_one(sql, api_key)

    return bool(result)


async def check_session(session: str) -> tuple[bool, bool]:
    """Проверка существования сессии и ее авторизации"""

    sql = "SELECT dnevnik_token, person_id, group_id FROM sessions WHERE session = $1"
    result = await Database.fetch_row(sql, session)

    if not result:
        await log(None, 'scheckSession', session, f"Session not found")
        return False, False

    try:
        async with AsyncDiaryAPI(token=result['dnevnik_token']) as dn:
            person_id: int = (await dn.get_info())['personId']
            groups: list[dict] = await dn.get_person_groups(person_id)
            group_id: int = filter(lambda g: g['type'] == 'Group', groups).__next__()['id']  # Класс ученика

    except (AsyncDiaryError, KeyError, StopIteration) as e:
        await log(None, 'scheckSession', session, f"{e.__class__.__name__}: {e}")
        return True, False

    authorized = person_id == result['person_id'] and group_id == result['group_id']
    if not authorized:
        await log(None, 'scheckSession', session, f"person_id={person_id}, group_id={group_id}")

    return True, authorized


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
