import pytest

from src.support.repositories.child_repository import ChildRepository


@pytest.mark.asyncio
async def test_create_child(
    child_repository: ChildRepository
):
    result = await child_repository.create_child(
        child_id=100001,
        school_id=500,
        group_id=10,
        timezone=10800
    )

    assert result is not None

    assert result.child_id == 100001
    assert result.school_id == 500
    assert result.group_id == 10
    assert result.timezone == 10800


@pytest.mark.asyncio
async def test_create_child_with_security_updates_existing(
    child_repository: ChildRepository,
    child
):
    result = await child_repository.create_child(
        child_id=child.child_id,
        school_id=999,
        group_id=777,
        timezone=3600,
        security=True
    )

    assert result is not None

    assert result.child_id == child.child_id
    assert result.school_id == 999
    assert result.group_id == 777
    assert result.timezone == 3600


@pytest.mark.asyncio
async def test_get_child(
    child_repository: ChildRepository,
    child
):
    result = await child_repository.get_child(
        child.child_id
    )

    assert result is not None

    assert result.child_id == child.child_id
    assert result.school_id == child.school_id
    assert result.group_id == child.group_id
    assert result.timezone == child.timezone


@pytest.mark.asyncio
async def test_get_unknown_child_returns_none(
    child_repository: ChildRepository
):
    result = await child_repository.get_child(
        999999
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_child(
    child_repository: ChildRepository,
    child
):
    result = await child_repository.update_child(
        child.child_id,
        school_id=999,
        group_id=777,
        timezone=3600
    )

    assert result is not None

    assert result.school_id == 999
    assert result.group_id == 777
    assert result.timezone == 3600


@pytest.mark.asyncio
async def test_update_child_partial(
    child_repository: ChildRepository,
    child
):
    result = await child_repository.update_child(
        child.child_id,
        timezone=3600
    )

    assert result is not None

    assert result.school_id == child.school_id
    assert result.group_id == child.group_id
    assert result.timezone == 3600


@pytest.mark.asyncio
async def test_update_unknown_child_returns_none(
    child_repository: ChildRepository
):
    result = await child_repository.update_child(
        999999,
        timezone=3600
    )

    assert result is None
