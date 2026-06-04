import pytest

from src.models.hours_type import HoursType
from src.support.repositories.hour_repository import HourRepository


def hour_factory(
    school_id: int,
    *,
    months: list[int] = None,
    weekdays: list[int] = None,
    hours: list[HoursType] = None,
    **kwargs
):
    if months is None:
        months = [9, 10, 11]
    if weekdays is None:
        weekdays = [1, 2, 3, 4, 5]
    if hours is None:
        hours = [
            HoursType(
                start="08:00",
                end="08:45",
                string="08:00 - 08:45"
            )
        ]

    return {
        "school_id": school_id,
        "months": months,
        "weekdays": weekdays,
        "hours": hours,
        **kwargs
    }


@pytest.fixture
def hour_repository(session):
    return HourRepository(session)


@pytest.fixture
async def hour(
    hour_repository: HourRepository
):
    return await hour_repository.create(
        hour_factory(
            school_id=100
        )
    )


@pytest.fixture
async def school_hours(
    hour_repository: HourRepository
):
    return await hour_repository.create_many([
        hour_factory(
            school_id=100,
            months=[9, 10],
            weekdays=[1, 2, 3]
        ),
        hour_factory(
            school_id=100,
            months=[12],
            weekdays=[4, 5]
        ),
        hour_factory(
            school_id=200,
            months=[9],
            weekdays=[1]
        )
    ])


@pytest.mark.asyncio
async def test_get_school_hours(
    hour_repository: HourRepository,
    school_hours
):
    result = await hour_repository.get_school_hours(
        100
    )

    assert len(result) == 2

    assert all(
        hour.school_id == 100
        for hour in result
    )


@pytest.mark.asyncio
async def test_get_school_hours_returns_empty(
    hour_repository: HourRepository
):
    result = await hour_repository.get_school_hours(
        999
    )

    assert result == []