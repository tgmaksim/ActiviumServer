import pytest

from datetime import datetime, UTC

from sqlalchemy.exc import IntegrityError

from ..factories import extracurricular_activity_factory, ea_processing_notification_factory

from src.support.repositories.extracurricular_activity_repository import ExtracurricularActivityRepository
from src.support.repositories.ea_processing_notification_repository import EAProcessingNotificationRepository


@pytest.mark.asyncio
async def test_create_extracurricular_activity_creates_notification(
    extracurricular_activity_repository: ExtracurricularActivityRepository,
    ea_processing_notification_repository: EAProcessingNotificationRepository,
):
    activity = await (
        extracurricular_activity_repository.create(
            extracurricular_activity_factory(
                school_id=100,
                group_id=10,
                start_time=datetime(
                    2030, 1, 1, 14, 0,
                    tzinfo=UTC
                )
            )
        )
    )

    notifications = await (
        ea_processing_notification_repository.get_multi()
    )

    assert len(notifications) == 1

    assert notifications[0].ea_id == activity.ea_id
    assert notifications[0].start_time == activity.start_time


@pytest.mark.asyncio
async def test_create_notification_with_unknown_activity_raises_error(
    ea_processing_notification_repository: EAProcessingNotificationRepository
):
    with pytest.raises(IntegrityError):
        await ea_processing_notification_repository.create(
            ea_processing_notification_factory(
                ea_id=999,
                start_time=datetime.now(UTC)
            )
        )


@pytest.mark.asyncio
async def test_get_next_extracurricular_activities(
    ea_processing_notification_repository: EAProcessingNotificationRepository,
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
    ea_processing_notification_repository: EAProcessingNotificationRepository,
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
    ea_processing_notification_repository: EAProcessingNotificationRepository,
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
    ea_processing_notification_repository: EAProcessingNotificationRepository,
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
