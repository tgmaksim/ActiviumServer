from typing import Optional
from database import Database
from datetime import datetime, UTC


async def log(ip: Optional[str], path: Optional[str], session: Optional[str], value: Optional[str]):
    sql = "INSERT INTO logging (ip, path, session, value, datetime) VALUES ($1, $2, $3, $4, $5)"
    await Database.execute(sql, ip, path, session, value, datetime.now(UTC).replace(tzinfo=None))


def get_bells_schedule(date: datetime):
    if date.weekday() in (0, 3):  # Понедельник и четверг
        return [
            "08:30 - 10:05",
            "10:20 - 11:55",
            "12:10 - 13:35",
            "13:50 - 15:15"
        ]
    elif date.weekday() == 6:  # Суббота
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
