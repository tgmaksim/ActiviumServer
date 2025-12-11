from typing import Optional
from database import Database
from datetime import datetime, UTC
from fastapi.requests import Request


async def log(request: Optional[Request], path: Optional[str], session: Optional[str], value: Optional[str]):
    ip = request.headers.get('x-forwarded-for') if request else None
    sql = "INSERT INTO logging (ip, path, session, value, datetime) VALUES ($1, $2, $3, $4, $5)"
    await Database.execute(sql, ip, path, session, value, datetime.now(UTC).replace(tzinfo=None))


async def get_min_version() -> dict[str, int]:
    """Получает последнюю доступную и поддерживающуюся со стороны сервера версии"""

    sql = """
            SELECT
                t.latest_version,
                t.min_api_version,
                v.logs as update_log
            FROM (
                SELECT
                    MAX(version) AS latest_version,
                    MAX(CASE WHEN flag = 'minAPI' THEN version END) AS min_api_version
                FROM versions
            ) t
            JOIN versions v ON v.version = t.latest_version;
          """
    result = await Database.fetch_row(sql)

    return {
        'latestVersion': result['latest_version'],
        'minApiVersion': result['min_api_version'],
        'updateLog': result['update_log']
    }


def get_bells_schedule(date: datetime):
    if date.weekday() in (0, 3):  # Понедельник и четверг
        return [
            dict(start="08:30", end="10:05"),
            dict(start="10:20", end="11:55"),
            dict(start="12:10", end="13:35"),
            dict(start="13:50", end="15:15"),
        ]
    elif date.weekday() == 5:  # Суббота
        return [
            dict(start="08:00", end="09:25"),
            dict(start="09:35", end="11:00"),
            dict(start="11:10", end="12:35"),
            dict(start="12:45", end="14:10"),
        ]
    else:  # Вторник, среда, пятница
        if date.month in (9, 10, 4, 5, 6, 7, 8):  # Первая и четвертая четверти
            return [
                dict(start="08:00", end="09:35"),
                dict(start="09:50", end="11:25"),
                dict(start="11:40", end="13:05"),
                dict(start="13:20", end="14:45"),
            ]
        else:  # Вторая и третья четверти
            return [
                dict(start="08:00", end="09:45"),
                dict(start="10:00", end="11:45"),
                dict(start="12:00", end="13:35"),
                dict(start="13:50", end="15:15"),
            ]
