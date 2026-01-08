import asyncpg

from hashlib import sha256
from typing import Optional
from datetime import datetime

from database import Database

from api.core import SESSION_LIFETIME


__all__ = ['create_session', 'auth_session']


async def create_session(session: Optional[str] = None) -> str:
    """
    Создание новой сессии и возврат ее идентификатора

    :param session: строковый идентификатор сессии, если требуется повторно авторизовать
    :return: строковый идентификатор новой сессии или входной, если она существует
    """

    sql = f"SELECT NOW() - datetime < INTERVAL '{SESSION_LIFETIME} days' FROM sessions WHERE session = $1"
    exists = await Database.fetch_row_for_one(sql, session)

    if session and exists:
        sql = "UPDATE sessions SET dnevnik_token = NULL WHERE session = $1"
    else:
        session = sha256(str(datetime.now()).encode('utf-8')).hexdigest()
        sql = ("INSERT INTO sessions (session, dnevnik_token, person_id, group_id, gymnasium_id, timezone, datetime) "
               "VALUES ($1, NULL, NULL, NULL, NULL, NULL, NOW())")

    await Database.execute(sql, session)

    return session


async def auth_session(
        session: str,
        dnevnik_token: str,
        person_id: int,
        group_id: int,
        gymnasium_id: int,
        timezone: int
) -> bool:
    """
    Авторизация сессии и возврат результата операции

    :param session: строковый идентификатор сессии
    :param dnevnik_token: токен для взаимодействия с аккаунтом дневника.ру
    :param person_id: идентификатор person в дневнике.ру
    :param group_id: идентификатор класса ученика(цы) в дневнике.ру
    :param gymnasium_id: идентификатор школы ученика(цы) в дневнике.ру
    :param timezone: часовой пояс
    :return: результат операции
    """

    sql = "SELECT true FROM sessions WHERE session = $1"
    exists = await Database.fetch_row_for_one(sql, session)
    if not exists:
        return False  # Сессия не существует

    try:
        sql = ("UPDATE sessions SET dnevnik_token = $1, person_id = $2, group_id = $3, gymnasium_id = $4, "
               "timezone = $5, datetime=NOW() WHERE session = $6")
        await Database.execute(sql, dnevnik_token, person_id, group_id, gymnasium_id, timezone, session)
    except asyncpg.exceptions.StringDataRightTruncationError:
        return False  # Переполнение длины dnevnik_token

    return True
