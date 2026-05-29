import pytest

from src.models.log_model import Log
from src.models.notification_model import Notification

from src.repositories.log_repository import LogRepository
from src.repositories.notification_repository import NotificationRepository


@pytest.fixture
def notification_repository(session):
    return NotificationRepository(session)


@pytest.fixture
async def notifications(
    log_repository: LogRepository,
    notification_repository: NotificationRepository
):
    await log_repository.add_log(
        ip="127.0.0.1",
        path="/api/1",
        session_id="session_1",
        status=True,
        method="GET",
        value="success"
    )

    await log_repository.add_log(
        ip="127.0.0.1",
        path="/api/2",
        session_id="session_2",
        status=False,
        method="POST",
        value="error"
    )

    await log_repository.add_log(
        ip="127.0.0.1",
        path="/api/3",
        session_id="session_3",
        status=True,
        method="DELETE",
        value="success 2"
    )

    return await notification_repository.get_multi()


@pytest.mark.asyncio
async def test_trigger_create_notification(
    notification_repository: NotificationRepository,
    log
):
    notification = await notification_repository.get_single(
        Notification.log_id == log.log_id
    )

    assert notification is not None

    assert notification.log_id == log.log_id
    assert notification.ip == log.ip
    assert notification.path == log.path
    assert notification.session_id == log.session_id
    assert notification.status == log.status
    assert notification.method == log.method
    assert notification.value == log.value


@pytest.mark.asyncio
async def test_get_count(
    notification_repository: NotificationRepository,
    notifications
):
    count_all, max_created_at, min_created_at, count_errors = (
        await notification_repository.get_count()
    )

    assert count_all == 3
    assert count_errors == 1

    assert max_created_at is not None
    assert min_created_at is not None

    assert max_created_at >= min_created_at


@pytest.mark.asyncio
async def test_delete_notifications(
    notification_repository: NotificationRepository,
    notifications
):
    _, max_created_at, _, _ = await notification_repository.get_count()

    deleted = await notification_repository.delete_notifications(
        max_created_at
    )

    assert deleted == 3

    result = await notification_repository.get_multi()

    assert result == []


@pytest.mark.asyncio
async def test_delete_log_cascade_notification(
    log_repository: LogRepository,
    notification_repository: NotificationRepository,
    log
):
    notification_before = await notification_repository.get_single(
        Notification.log_id == log.log_id
    )

    assert notification_before is not None

    await log_repository.delete(
        Log.log_id == log.log_id
    )

    notification_after = await notification_repository.get_single(
        Notification.log_id == log.log_id
    )

    assert notification_after is None