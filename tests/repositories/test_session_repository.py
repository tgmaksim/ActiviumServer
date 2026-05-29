import pytest

from datetime import timedelta

from sqlalchemy.exc import IntegrityError

from src.models.child_model import Child
from src.models.parent_model import Parent

from src.support.repositories.child_repository import ChildRepository
from src.support.repositories.parent_repository import ParentRepository
from src.support.repositories.session_repository import SessionRepository


@pytest.fixture
async def app_session(
    session_repository: SessionRepository
):
    await session_repository.create_session(
        "session_1"
    )

    return await session_repository.get_session(
        "session_1",
        only_life=False
    )


@pytest.mark.asyncio
async def test_create_session(
    session_repository: SessionRepository
):
    await session_repository.create_session(
        "session_1"
    )

    result = await session_repository.get_session(
        "session_1",
        only_life=False
    )

    assert result is not None

    assert result.session_id == "session_1"
    assert result.life is True


@pytest.mark.asyncio
async def test_get_unknown_session_returns_none(
    session_repository: SessionRepository
):
    result = await session_repository.get_session(
        "unknown"
    )

    assert result is None


@pytest.mark.asyncio
async def test_auth_session(
    session_repository: SessionRepository,
    app_session,
    parent,
    child
):
    result = await session_repository.auth_session(
        session_id=app_session.session_id,
        dnevnik_token="token",
        parent_id=parent.parent_id,
        active_child_id=child.child_id
    )

    assert result is not None

    assert result.parent_id == parent.parent_id
    assert result.active_child_id == child.child_id
    assert result.dnevnik_token == "token"
    assert result.life is True


@pytest.mark.asyncio
async def test_get_sessions(
    session_repository: SessionRepository,
    auth_session
):
    result = await session_repository.get_sessions(
        auth_session.parent_id
    )

    assert len(result) == 1

    assert result[0].session_id == auth_session.session_id


@pytest.mark.asyncio
async def test_get_sessions_returns_only_life_sessions(
    session_repository: SessionRepository,
    auth_session
):
    await session_repository.kill_session(
        auth_session.session_id
    )

    result = await session_repository.get_sessions(
        auth_session.parent_id
    )

    assert result == []


@pytest.mark.asyncio
async def test_update_firebase(
    session_repository: SessionRepository,
    app_session
):
    result = await session_repository.update_firebase(
        app_session.session_id,
        "firebase_token"
    )

    assert result.firebase_token == "firebase_token"


@pytest.mark.asyncio
async def test_set_active_child(
    session_repository: SessionRepository,
    child_repository: ChildRepository,
    app_session,
    parent,
    child
):
    await session_repository.auth_session(
        session_id=app_session.session_id,
        dnevnik_token="token",
        parent_id=parent.parent_id,
        active_child_id=child.child_id
    )

    new_child_id = 999999

    second_child = await child_repository.create_child(
        child_id=new_child_id,
        school_id=500,
        group_id=11,
        timezone=10800
    )

    result = await session_repository.set_active_child(
        app_session.session_id,
        second_child.child_id
    )

    assert result.active_child_id == second_child.child_id


@pytest.mark.asyncio
async def test_kill_session(
    session_repository: SessionRepository,
    auth_session
):
    result = await session_repository.kill_session(
        auth_session.session_id
    )

    assert result.life is False


@pytest.mark.asyncio
async def test_get_session_returns_none_for_dead_session(
    session_repository: SessionRepository,
    auth_session
):
    await session_repository.kill_session(
        auth_session.session_id
    )

    result = await session_repository.get_session(
        auth_session.session_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_session_with_only_life_false_returns_dead_session(
    session_repository: SessionRepository,
    auth_session
):
    await session_repository.kill_session(
        auth_session.session_id
    )

    result = await session_repository.get_session(
        auth_session.session_id,
        only_life=False
    )

    assert result is not None
    assert result.life is False


@pytest.mark.asyncio
async def test_auth_session_without_child_raises_error(
    session_repository: SessionRepository,
    app_session,
    parent
):
    with pytest.raises(IntegrityError):
        await session_repository.auth_session(
            session_id=app_session.session_id,
            dnevnik_token="token",
            parent_id=parent.parent_id,
            active_child_id=None
        )


@pytest.mark.asyncio
async def test_auth_session_with_unknown_parent_raises_error(
    session_repository: SessionRepository,
    app_session,
    child
):
    with pytest.raises(IntegrityError):
        await session_repository.auth_session(
            session_id=app_session.session_id,
            dnevnik_token="token",
            parent_id=999999,
            active_child_id=child.child_id
        )


@pytest.mark.asyncio
async def test_auth_session_with_unknown_child_raises_error(
    session_repository: SessionRepository,
    app_session,
    parent
):
    with pytest.raises(IntegrityError):
        await session_repository.auth_session(
            session_id=app_session.session_id,
            dnevnik_token="token",
            parent_id=parent.parent_id,
            active_child_id=999999
        )


@pytest.mark.asyncio
async def test_delete_parent_cascades_sessions(
    session_repository: SessionRepository,
    parent_repository: ParentRepository,
    auth_session,
    parent
):
    await parent_repository.delete(
        Parent.parent_id == parent.parent_id
    )

    result = await session_repository.get_session(
        auth_session.session_id,
        only_life=False
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_active_child_raises_error(
    child_repository: ChildRepository,
    auth_session,
    child
):
    with pytest.raises(IntegrityError):
        await child_repository.delete(
            Child.child_id == child.child_id
        )


@pytest.mark.asyncio
async def test_kill_old_sessions(
    session_repository: SessionRepository,
    auth_session
):
    await session_repository.kill_old_sessions(
        timedelta(days=-1)
    )

    result = await session_repository.get_session(
        auth_session.session_id,
        only_life=False
    )

    assert result.life is False
