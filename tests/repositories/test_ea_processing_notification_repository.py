import pytest

from datetime import datetime, UTC

from ..factories import extracurricular_activity_factory
from ..fixtures import ea_processing_notification_repository, ea_processing_notifications, extracurricular_activity_repository


@pytest.mark.asyncio
async def test_get_next_extracurricular_activities(
    ea_processing_notification_repository,
    ea_processing_notifications
):
    result = await (
        ea_processing_notification_repository
        .get_next_extracurricular_activities(
            (
                datetime(
                    2028, 1, 10,
                    tzinfo=UTC
                ),
                datetime(
                    2028, 1, 11,
                    tzinfo=UTC
                )
            )
        )
    )

    assert len(result) == 2

    assert all(
        activity.start_time ==
        datetime(
            2028, 1, 10, 14, 0,
            tzinfo=UTC
        )
        for activity in result
    )


@pytest.mark.asyncio
async def test_get_next_extracurricular_activities_returns_empty(
    ea_processing_notification_repository,
    ea_processing_notifications
):
    result = await (
        ea_processing_notification_repository
        .get_next_extracurricular_activities(
            (
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
async def test_finish_process(
    ea_processing_notification_repository,
    ea_processing_notifications
):
    notification = ea_processing_notifications[0]

    await ea_processing_notification_repository.finish_process(
        notification.ea_id
    )

    result = await (
        ea_processing_notification_repository
        .get_next_extracurricular_activities(
            (
                datetime(
                    2028, 1, 10,
                    tzinfo=UTC
                ),
                datetime(
                    2028, 1, 11,
                    tzinfo=UTC
                )
            )
        )
    )

    assert len(result) == 1


@pytest.mark.asyncio
async def test_delete_overdue_ea(
    ea_processing_notification_repository,
    extracurricular_activity_repository
):
    await extracurricular_activity_repository.create(
        extracurricular_activity_factory(
            school_id=100,
            group_id=1,
            start_time=datetime(
                2020, 1, 1,
                tzinfo=UTC
            )
        )
    )

    await (
        ea_processing_notification_repository
        .delete_overdue_ea()
    )

    result = await (
        ea_processing_notification_repository
        .get_next_extracurricular_activities(
            (
                datetime(
                    2019, 1, 1,
                    tzinfo=UTC
                ),
                datetime(
                    2021, 1, 1,
                    tzinfo=UTC
                )
            )
        )
    )

    assert result == []
