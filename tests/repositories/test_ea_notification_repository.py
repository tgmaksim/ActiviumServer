import pytest

from sqlalchemy.exc import IntegrityError

from src.models.session_model import Session

from src.support.repositories.child_repository import ChildRepository
from src.support.repositories.session_repository import SessionRepository
from src.support.repositories.ea_notification_repository import EANotificationRepository


@pytest.fixture
def ea_notification_repository(session):
    return EANotificationRepository(session)


@pytest.fixture
async def ea_notification(
    ea_notification_repository: EANotificationRepository,
    auth_session,
    child
):
    return await ea_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )


@pytest.mark.asyncio
async def test_turn_on(
    ea_notification_repository: EANotificationRepository,
    auth_session,
    child
):
    result = await ea_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    assert result is not None

    assert result.session_id == auth_session.session_id
    assert result.child_id == child.child_id


@pytest.mark.asyncio
async def test_turn_on_duplicate_returns_existing(
    ea_notification_repository: EANotificationRepository,
    ea_notification,
    auth_session,
    child
):
    result = await ea_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    notifications = await ea_notification_repository.get_multi()

    assert result is None

    assert len(notifications) == 1


@pytest.mark.asyncio
async def test_get_status(
    ea_notification_repository: EANotificationRepository,
    ea_notification,
    auth_session,
    child
):
    result = await ea_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
    )

    assert result is not None

    assert result.session_id == auth_session.session_id
    assert result.child_id == child.child_id


@pytest.mark.asyncio
async def test_get_unknown_status_returns_none(
    ea_notification_repository: EANotificationRepository
):
    result = await ea_notification_repository.get_status(
        "unknown",
        999999
    )

    assert result is None


@pytest.mark.asyncio
async def test_turn_off(
    ea_notification_repository: EANotificationRepository,
    ea_notification,
    auth_session,
    child
):
    await ea_notification_repository.turn_off(
        auth_session.session_id,
        child.child_id
    )

    result = await ea_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_notifications(
    ea_notification_repository: EANotificationRepository,
    child_repository: ChildRepository,
    auth_session,
    child
):
    await ea_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    second_child = await child_repository.create_child(
        child_id=200002,
        school_id=500,
        group_id=20,
        timezone=10800
    )

    await ea_notification_repository.turn_on(
        auth_session.session_id,
        second_child.child_id
    )

    result = await ea_notification_repository.get_notifications([
        (500, 10)
    ])

    assert len(result) == 1

    assert result[0].child_id == child.child_id


@pytest.mark.asyncio
async def test_get_notifications_multiple_groups(
    ea_notification_repository: EANotificationRepository,
    child_repository: ChildRepository,
    auth_session,
    child
):
    await ea_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    second_child = await child_repository.create_child(
        child_id=200002,
        school_id=500,
        group_id=20,
        timezone=10800
    )

    await ea_notification_repository.turn_on(
        auth_session.session_id,
        second_child.child_id
    )

    result = await ea_notification_repository.get_notifications([
        (500, 10),
        (500, 20)
    ])

    assert len(result) == 2


@pytest.mark.asyncio
async def test_turn_on_unknown_session_raises_error(
    ea_notification_repository: EANotificationRepository,
    child
):
    with pytest.raises(IntegrityError):
        await ea_notification_repository.turn_on(
            "unknown",
            child.child_id
        )


@pytest.mark.asyncio
async def test_turn_on_unknown_child_raises_error(
    ea_notification_repository: EANotificationRepository,
    auth_session
):
    with pytest.raises(IntegrityError):
        await ea_notification_repository.turn_on(
            auth_session.session_id,
            999999
        )


@pytest.mark.asyncio
async def test_delete_session_cascades_notifications(
    session_repository: SessionRepository,
    ea_notification_repository: EANotificationRepository,
    ea_notification,
    auth_session,
    child
):
    await session_repository.delete(
        Session.session_id == auth_session.session_id
    )

    result = await ea_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_child_cascades_notifications(
    session_repository: SessionRepository,
    ea_notification_repository: EANotificationRepository,
    ea_notification,
    auth_session,
    child
):
    await session_repository.delete(
        Session.session_id == auth_session.session_id
    )

    result = await ea_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
    )

    assert result is None
