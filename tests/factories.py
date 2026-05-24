from datetime import datetime


def version_factory(
    number: int,
    version: str,
    **kwargs
):
    return {
        "number": number,
        "version": version,
        "status_id": kwargs.get("status_id", 0.5),
        "status": kwargs.get("status", "test"),
        "logs": kwargs.get("logs", "test logs"),
        "date": kwargs.get("date", "09.12.2009"),
        **kwargs
    }


def tgbot_state_factory(
    key: str,
    **kwargs
):
    return {
        "key": key,
        "state": kwargs.get("state", "waiting_message"),
        "data": kwargs.get("data", {}),
        **kwargs
    }


def hour_factory(
    school_id: int,
    **kwargs
):
    return {
        "school_id": school_id,
        "months": kwargs.get("months", [9, 10, 11]),
        "weekdays": kwargs.get("weekdays", [1, 2, 3, 4, 5]),
        "hours": kwargs.get(
            "hours",
            [
                {
                    "lesson": 1,
                    "start": "08:00",
                    "end": "08:45"
                }
            ]
        ),
        **kwargs
    }


def school_admin_factory(
    user_id: int,
    name: str,
    **kwargs
):
    return {
        "user_id": user_id,
        "name": name,
        "parent_admin_id": kwargs.get("parent_admin_id"),
        "person_id": kwargs.get("person_id"),
        "school_id": kwargs.get("school_id"),
        "timezone": kwargs.get("timezone"),
        "dnevnik_token": kwargs.get("dnevnik_token"),
        **kwargs
    }


def extracurricular_activity_factory(
    school_id: int,
    group_id: int,
    start_time: datetime,
    **kwargs
):
    return {
        "school_id": school_id,
        "group_id": group_id,
        "start_time": start_time,
        "subject": kwargs.get("subject", "Math"),
        "place": kwargs.get("place", "101"),
        "hours": kwargs.get(
            "hours",
            {
                "start": "14:00",
                "end": "15:00"
            }
        ),
        **kwargs
    }


def ea_processing_notification_factory(
    ea_id: int,
    start_time: datetime,
    **kwargs
):
    return {
        "ea_id": ea_id,
        "start_time": start_time,
        **kwargs
    }
