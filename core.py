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
                v.logs as update_log,
                v.sha256
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
        'updateLog': result['update_log'],
        'sha256': result['sha256']
    }


def get_bells_schedule(date: datetime):
    if date.weekday() in (0, 3):  # Понедельник и четверг
        return [
            "08:30 - 10:05",
            "10:20 - 11:55",
            "12:10 - 13:35",
            "13:50 - 15:15"
        ]
    elif date.weekday() == 5:  # Суббота
        return [
            "08:00 - 09:25",
            "09:35 - 11:00",
            "11:10 - 12:35",
            "12:45 - 14:10"
        ]
    else:  # Вторник, среда, пятница
        if date.month in (9, 10, 4, 5, 6, 7, 8):  # Первая и четвертая четверти
            return [
                "08:00 - 09:35",
                "09:50 - 11:25",
                "11:40 - 13:05",
                "13:20 - 14:45"
            ]
        else:  # Вторая и третья четверти
            return [
                "08:00 - 09:45",
                "10:00 - 11:45",
                "12:00 - 13:35",
                "13:50 - 15:15"
            ]
