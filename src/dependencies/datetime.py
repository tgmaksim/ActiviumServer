from datetime import datetime, timedelta, timezone


__all__ = ['datetime_now', 'astimezone']


def datetime_now(tz_seconds_offset: int = 0) -> datetime:
    """Текущее время в часом поясе"""

    return datetime.now(timezone(timedelta(seconds=tz_seconds_offset)))


def astimezone(dt: datetime, tz_seconds_offset: int) -> datetime:
    """Перевод времени в другой часовой пояс, при отсутствии начального часового пояса считается UTC"""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(seconds=tz_seconds_offset)))
    return dt.astimezone(timezone(timedelta(seconds=tz_seconds_offset)))
