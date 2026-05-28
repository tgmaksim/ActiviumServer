import pytest

from src.support.repositories.hour_repository import HourRepository


@pytest.mark.asyncio
async def test_get_hours(
    hour_repository: HourRepository,
    hour
):
    result = await hour_repository.get_hours(
        school_id=100,
        month=9,
        weekday=1
    )

    assert result is not None

    assert result.school_id == 100
    assert 9 in result.months
    assert 1 in result.weekdays


@pytest.mark.asyncio
async def test_get_hours_returns_none_for_unknown_school(
    hour_repository: HourRepository,
    hour
):
    result = await hour_repository.get_hours(
        school_id=999,
        month=9,
        weekday=1
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_hours_returns_none_for_unknown_month(
    hour_repository: HourRepository,
    hour
):
    result = await hour_repository.get_hours(
        school_id=100,
        month=12,
        weekday=1
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_hours_returns_none_for_unknown_weekday(
    hour_repository: HourRepository,
    hour
):
    result = await hour_repository.get_hours(
        school_id=100,
        month=9,
        weekday=7
    )

    assert result is None


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