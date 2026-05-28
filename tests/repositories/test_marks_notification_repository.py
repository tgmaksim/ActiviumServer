import pytest

from datetime import datetime, UTC

from sqlalchemy.exc import IntegrityError

from src.models.session_model import Session

from src.support.repositories.child_repository import ChildRepository
from src.support.repositories.session_repository import SessionRepository
from src.support.repositories.marks_notification_repository import MarksNotificationRepository


@pytest.mark.asyncio
async def test_turn_on(
    marks_notification_repository: MarksNotificationRepository,
    auth_session,
    child
):
    result = await marks_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    assert result is not None

    assert result.session_id == auth_session.session_id
    assert result.child_id == child.child_id

    assert result.last_mark is not None


@pytest.mark.asyncio
async def test_turn_on_duplicate_returns_none(
    marks_notification_repository: MarksNotificationRepository,
    marks_notification,
    auth_session,
    child
):
    result = await marks_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    notifications = await marks_notification_repository.get_multi()

    assert result is None

    assert len(notifications) == 1


@pytest.mark.asyncio
async def test_turn_on_duplicate_returns_none(
    marks_notification_repository: MarksNotificationRepository,
    marks_notification,
    auth_session,
    child
):
    result = await marks_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    notifications = await marks_notification_repository.get_multi()

    assert result is None

    assert len(notifications) == 1


@pytest.mark.asyncio
async def test_get_count(
    marks_notification_repository: MarksNotificationRepository,
    marks_notification
):
    result = await marks_notification_repository.get_count()

    assert result == 1


@pytest.mark.asyncio
async def test_get_empty_count(
    marks_notification_repository: MarksNotificationRepository
):
    result = await marks_notification_repository.get_count()

    assert result == 0


@pytest.mark.asyncio
async def test_get_next_child(
    child_repository: ChildRepository,
    marks_notification_repository: MarksNotificationRepository,
    auth_session,
    child
):
    await marks_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    second_child = await child_repository.create_child(
        child_id=200002,
        school_id=500,
        group_id=20,
        timezone=10800
    )

    await marks_notification_repository.turn_on(
        auth_session.session_id,
        second_child.child_id
    )

    result = await marks_notification_repository.get_next_child()

    assert len(result) == 1

    assert result[0].child_id == child.child_id


@pytest.mark.asyncio
async def test_get_next_child_returns_all_child_notifications(
    session_repository: SessionRepository,
    marks_notification_repository: MarksNotificationRepository,
    auth_session,
    child,
    parent
):
    await marks_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    await session_repository.create_session(
        "session_2"
    )

    await session_repository.auth_session(
        session_id="session_2",
        dnevnik_token="token",
        parent_id=parent.parent_id,
        active_child_id=child.child_id
    )

    await marks_notification_repository.turn_on(
        "session_2",
        child.child_id
    )

    result = await marks_notification_repository.get_next_child()

    assert len(result) == 2

    assert all(
        notification.child_id == child.child_id
        for notification in result
    )


@pytest.mark.asyncio
async def test_update_date(
    marks_notification_repository: MarksNotificationRepository,
    marks_notification,
    auth_session,
    child
):
    new_date = datetime(
        2028, 1, 10, 12, 0,
        tzinfo=UTC
    )

    await marks_notification_repository.update_date(
        child.child_id,
        new_date
    )

    result = await marks_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
    )

    assert result.last_mark == new_date


@pytest.mark.asyncio
async def test_update_date_none_keeps_old_value(
    marks_notification_repository: MarksNotificationRepository,
    marks_notification,
    auth_session,
    child
):
    old_date = marks_notification.last_mark

    await marks_notification_repository.update_date(
        child.child_id,
        None
    )

    result = await marks_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
    )

    assert result.last_mark == old_date


@pytest.mark.asyncio
async def test_turn_on_unknown_session_raises_error(
    marks_notification_repository: MarksNotificationRepository,
    child
):
    with pytest.raises(IntegrityError):
        await marks_notification_repository.turn_on(
            "unknown",
            child.child_id
        )


@pytest.mark.asyncio
async def test_turn_on_unknown_child_raises_error(
    marks_notification_repository: MarksNotificationRepository,
    auth_session
):
    with pytest.raises(IntegrityError):
        await marks_notification_repository.turn_on(
            auth_session.session_id,
            999999
        )


@pytest.mark.asyncio
async def test_delete_session_cascades_notifications(
    session_repository: SessionRepository,
    marks_notification_repository: MarksNotificationRepository,
    marks_notification,
    auth_session,
    child
):
    await session_repository.delete(
        Session.session_id == auth_session.session_id
    )

    result = await marks_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
    )

    assert result is None
