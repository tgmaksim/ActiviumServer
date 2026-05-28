import pytest

from sqlalchemy.exc import IntegrityError

from src.models.session_model import Session
from src.support.repositories.cache_repository import CacheRepository
from src.support.repositories.session_repository import SessionRepository


@pytest.mark.asyncio
async def test_put_cache(
    cache_repository: CacheRepository,
    auth_session,
    child
):
    result = await cache_repository.put_cache(
        auth_session.session_id,
        child.child_id,
        "profile",
        {"name": "Maksim"}
    )

    assert result is not None

    assert result.session_id == auth_session.session_id
    assert result.child_id == child.child_id
    assert result.key == "profile"
    assert result.value == {"name": "Maksim"}


@pytest.mark.asyncio
async def test_put_caches(
    cache_repository: CacheRepository,
    auth_session,
    child
):
    result = await cache_repository.put_caches(
        auth_session.session_id,
        child.child_id,
        [
            ("profile", {"name": "Maksim"}),
            ("lessons", [{"lesson": 1}])
        ]
    )

    assert len(result) == 2

    assert result[0].key == "profile"
    assert result[1].key == "lessons"


@pytest.mark.asyncio
async def test_put_cache_updates_existing(
    cache_repository: CacheRepository,
    auth_session,
    child
):
    await cache_repository.put_cache(
        auth_session.session_id,
        child.child_id,
        "profile",
        {"name": "Old"}
    )

    result = await cache_repository.put_cache(
        auth_session.session_id,
        child.child_id,
        "profile",
        {"name": "New"}
    )

    assert result.value == {"name": "New"}


@pytest.mark.asyncio
async def test_put_caches_updates_existing(
    cache_repository: CacheRepository,
    auth_session,
    child
):
    await cache_repository.put_caches(
        auth_session.session_id,
        child.child_id,
        [
            ("profile", {"name": "Old"}),
            ("lessons", [{"lesson": 1}])
        ]
    )

    result = await cache_repository.put_caches(
        auth_session.session_id,
        child.child_id,
        [
            ("profile", {"name": "New"})
        ]
    )

    assert len(result) == 1
    assert result[0].value == {"name": "New"}


@pytest.mark.asyncio
async def test_get_cache(
    cache_repository: CacheRepository,
    caches,
    auth_session,
    child
):
    result = await cache_repository.get_cache(
        auth_session.session_id,
        child.child_id,
        "profile"
    )

    assert result is not None

    assert result.key == "profile"
    assert result.value == {"name": "Maksim"}


@pytest.mark.asyncio
async def test_get_unknown_cache_returns_none(
    cache_repository: CacheRepository,
    auth_session,
    child
):
    result = await cache_repository.get_cache(
        auth_session.session_id,
        child.child_id,
        "unknown"
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_caches(
    cache_repository: CacheRepository,
    caches,
    auth_session,
    child
):
    result = await cache_repository.get_caches(
        auth_session.session_id,
        child.child_id,
        ["profile", "lessons"]
    )

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_caches_returns_only_requested_keys(
    cache_repository: CacheRepository,
    caches,
    auth_session,
    child
):
    result = await cache_repository.get_caches(
        auth_session.session_id,
        child.child_id,
        ["profile"]
    )

    assert len(result) == 1
    assert result[0].key == "profile"


@pytest.mark.asyncio
async def test_put_cache_with_unknown_session_raises_error(
    cache_repository: CacheRepository,
    child
):
    with pytest.raises(IntegrityError):
        await cache_repository.put_cache(
            "unknown",
            child.child_id,
            "profile",
            {}
        )


@pytest.mark.asyncio
async def test_put_cache_with_unknown_child_raises_error(
    cache_repository: CacheRepository,
    auth_session
):
    with pytest.raises(IntegrityError):
        await cache_repository.put_cache(
            auth_session.session_id,
            999999,
            "profile",
            {}
        )


@pytest.mark.asyncio
async def test_delete_session_cascades_caches(
    cache_repository: CacheRepository,
    session_repository: SessionRepository,
    caches,
    auth_session,
    child
):
    await session_repository.delete(
        Session.session_id == auth_session.session_id
    )

    result = await cache_repository.get_caches(
        auth_session.session_id,
        child.child_id,
        ["profile", "lessons"]
    )

    assert result == []


@pytest.mark.asyncio
async def test_delete_unregistered_cache(
    cache_repository: CacheRepository,
    session_repository: SessionRepository,
    caches,
    auth_session,
    child
):
    await session_repository.kill_session(
        auth_session.session_id
    )

    await cache_repository.delete_unregistered_cache()

    result = await cache_repository.get_caches(
        auth_session.session_id,
        child.child_id,
        ["profile", "lessons"]
    )

    assert result == []
