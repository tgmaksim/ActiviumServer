from typing import Optional
from datetime import datetime, timedelta, UTC, date

from database import Database

from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI


templates = Jinja2Templates(directory="templates")  # Папка с html-страницами
__all__ = ['templates', 'log', 'get_bells_schedule', 'datetime_now']


# В оригинальном методе баг
async def get_person_schedule(
    self: AsyncDiaryAPI,
    person_id,
    group_id,
    start_time: str = str(datetime.now()),
    end_time: str = str(datetime.now()),
):
    return await self.get(
        f"persons/{person_id}/groups/{group_id}/schedules",
        params={"startDate": start_time, "endDate": end_time},
    )


AsyncDiaryAPI.get_person_schedule = get_person_schedule


async def log(request: Optional[Request], path: Optional[str], session: Optional[str], value: Optional[str]):
    """
    Логирование информации в базу данных

    :param request: объект запроса ``Request`` для получения IP-адреса клиента
    :param path: путь к API-методу или web-странице
    :param session: строковый идентификатор сессии
    :param value: строковые данные для логирование
    """

    ip = request.headers.get('x-forwarded-for') if request else None  # Реальный IP-адрес клиента

    try:
        sql = "INSERT INTO logging (ip, path, session, value, datetime) VALUES ($1, $2, $3, $4, $5)"
        await Database.execute(sql, ip, path, session, value, datetime_now())
    except Exception as e:
        print(ip, path, session, value)
        print(e)


def datetime_now(tz_offset: int = 0) -> datetime:
    """
    Текущее время в определенном часовом поясе

    :param tz_offset: смещение часового пояса от UTC
    :return: объект даты и времени ``datetime`` в данный момент в данном часовом поясе
    """

    return datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=tz_offset)


def get_bells_schedule(day: date) -> list[dict[str, str]]:
    """
    Звонковое расписание в данный день

    :param day: дата дня, для которого требуется расписание звонков
    :return: список из времени урока: {"start": "00:00", "end": "00:00"}
    """

    # TODO: вынести в базу данных
    if day.weekday() in (0, 3):  # Понедельник и четверг
        return [
            dict(start="08:00", end="08:25"),

            dict(start="08:30", end="09:10"),
            dict(start="09:25", end="10:05"),

            dict(start="10:20", end="11:00"),
            dict(start="11:15", end="11:55"),

            dict(start="12:10", end="12:50"),
            dict(start="12:55", end="13:35"),

            dict(start="13:50", end="13:30"),
            dict(start="13:35", end="14:15")
        ]
    elif day.weekday() == 5:  # Суббота
        return [
            dict(start="08:00", end="08:40"),
            dict(start="08:45", end="09:25"),

            dict(start="09:35", end="10:05"),
            dict(start="10:10", end="11:00"),

            dict(start="11:10", end="11:50"),
            dict(start="11:55", end="12:35"),

            dict(start="12:45", end="12:25"),
            dict(start="12:30", end="13:10")
        ]
    else:  # Вторник, среда, пятница
        if day.month in (9, 10, 4, 5, 6, 7, 8):  # Первая и четвертая четверти
            return [
                dict(start="08:00", end="08:40"),
                dict(start="08:55", end="09:35"),

                dict(start="09:50", end="10:30"),
                dict(start="10:45", end="11:25"),

                dict(start="11:40", end="12:20"),
                dict(start="12:25", end="13:05"),

                dict(start="13:20", end="14:00"),
                dict(start="14:05", end="14:45"),
            ]
        else:  # Вторая и третья четверти
            return [
                dict(start="08:00", end="08:30"),
                dict(start="08:45", end="09:45"),  # Вторая и третья части

                dict(start="10:00", end="10:30"),
                dict(start="10:45", end="11:45"),  # Вторая и третья части

                dict(start="12:00", end="12:30"),
                dict(start="12:35", end="13:35"),  # Вторая и третья части

                dict(start="13:50", end="14:30"),
                dict(start="14:35", end="15:15")
            ]
