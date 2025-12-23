import asyncpg

from hashlib import sha256
from typing import Optional
from datetime import datetime

from database import Database


__all__ = ['create_session', 'auth_session']


async def create_session(session: Optional[str] = None) -> str:
    """Создание новой сессии и возврат ее идентификатора"""

    sql = "SELECT true FROM sessions WHERE session = $1 AND datetime - NOW() > INTERVAL '28 days'"
    exists = await Database.fetch_row_for_one(sql, session)

    if session and exists:
        sql = "UPDATE sessions SET dnevnik_token = NULL WHERE session = $1"
    else:
        session = sha256(str(datetime.now()).encode('utf-8')).hexdigest()
        sql = ("INSERT INTO sessions (session, dnevnik_token, person_id, group_id, datetime) "
               f"VALUES ($1, NULL, NULL, NULL, NOW())")

    await Database.execute(sql, session)

    return session


async def auth_session(session: str, token: str, person_id: int, group_id: int) -> bool:
    """Авторизация сессии и возврат результата операции"""

    sql = "SELECT true FROM sessions WHERE session = $1"
    exists = await Database.fetch_row_for_one(sql, session)
    if not exists:
        return False  # Сессия не существует

    try:
        sql = "UPDATE sessions SET dnevnik_token = $1, person_id = $2, group_id = $3, datetime=NOW() WHERE session = $4"
        await Database.execute(sql, token, person_id, group_id, session)

    except asyncpg.exceptions.StringDataRightTruncationError:
        return False  # Переполнение длины dnevnik_token

    return True
