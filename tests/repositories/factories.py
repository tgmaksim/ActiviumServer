from datetime import datetime

from src.models.hours_type import HoursType


__all__ = ['extracurricular_activity_factory']


def extracurricular_activity_factory(
        school_id: int,
        group_id: int,
        *,
        start_time: datetime,
        subject: str = "Math",
        place: str = "101",
        hours: HoursType = None,
        **kwargs
):
    if hours is None:
        hours = HoursType(
            start="14:00",
            end="15:00",
            string="14:00 - 15:00"
        )

    return {
        "school_id": school_id,
        "group_id": group_id,
        "start_time": start_time,
        "subject": subject,
        "place": place,
        "hours": hours,
        **kwargs
    }
