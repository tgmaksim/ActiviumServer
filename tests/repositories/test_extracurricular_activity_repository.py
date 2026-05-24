import pytest

from datetime import datetime, UTC

from ..fixtures import extracurricular_activity_repository, extracurricular_activities

from src.support.repositories.extracurricular_activity_repository import ExtracurricularActivityRepository


@pytest.mark.asyncio
async def test_get_extracurricular_activities(
    extracurricular_activity_repository: ExtracurricularActivityRepository,
    extracurricular_activities
):
    result = await (
        extracurricular_activity_repository
        .get_extracurricular_activities(
            school_id=100,
            group_id=10,
            period=(
                datetime(
                    2025, 9, 1,
                    tzinfo=UTC
                ),
                datetime(
                    2025, 9, 3,
                    tzinfo=UTC
                )
            )
        )
    )

    assert len(result) == 2

    assert all(
        activity.school_id == 100
        for activity in result
    )

    assert all(
        activity.group_id == 10
        for activity in result
    )


@pytest.mark.asyncio
async def test_get_extracurricular_activities_returns_empty_for_unknown_school(
    extracurricular_activity_repository: ExtracurricularActivityRepository,
    extracurricular_activities
):
    result = await (
        extracurricular_activity_repository
        .get_extracurricular_activities(
            school_id=999,
            group_id=10,
            period=(
                datetime(
                    2025, 9, 1,
                    tzinfo=UTC
                ),
                datetime(
                    2025, 9, 3,
                    tzinfo=UTC
                )
            )
        )
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_extracurricular_activities_returns_empty_for_unknown_group(
    extracurricular_activity_repository: ExtracurricularActivityRepository,
    extracurricular_activities
):
    result = await (
        extracurricular_activity_repository
        .get_extracurricular_activities(
            school_id=100,
            group_id=999,
            period=(
                datetime(
                    2025, 9, 1,
                    tzinfo=UTC
                ),
                datetime(
                    2025, 9, 3,
                    tzinfo=UTC
                )
            )
        )
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_extracurricular_activities_returns_empty_for_unknown_period(
    extracurricular_activity_repository: ExtracurricularActivityRepository,
    extracurricular_activities
):
    result = await (
        extracurricular_activity_repository
        .get_extracurricular_activities(
            school_id=100,
            group_id=10,
            period=(
                datetime(
                    2030, 1, 1,
                    tzinfo=UTC
                ),
                datetime(
                    2030, 1, 2,
                    tzinfo=UTC
                )
            )
        )
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_extracurricular_activities_sorted_by_start_time(
    extracurricular_activity_repository: ExtracurricularActivityRepository,
    extracurricular_activities
):
    result = await (
        extracurricular_activity_repository
        .get_extracurricular_activities(
            school_id=100,
            group_id=10,
            period=(
                datetime(
                    2025, 9, 1,
                    tzinfo=UTC
                ),
                datetime(
                    2025, 9, 3,
                    tzinfo=UTC
                )
            )
        )
    )

    assert result[0].start_time < result[1].start_time
