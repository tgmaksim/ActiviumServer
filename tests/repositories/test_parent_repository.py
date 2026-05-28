import pytest

from src.support.repositories.parent_repository import ParentRepository


@pytest.mark.asyncio
async def test_create_parent(
    parent_repository: ParentRepository
):
    result = await parent_repository.create_parent(
        100001
    )

    assert result is not None
    assert result.parent_id == 100001


@pytest.mark.asyncio
async def test_get_parent(
    parent_repository: ParentRepository,
    parent
):
    result = await parent_repository.get_parent(
        parent.parent_id
    )

    assert result is not None
    assert result.parent_id == parent.parent_id


@pytest.mark.asyncio
async def test_get_unknown_parent_returns_none(
    parent_repository: ParentRepository
):
    result = await parent_repository.get_parent(
        999999
    )

    assert result is None