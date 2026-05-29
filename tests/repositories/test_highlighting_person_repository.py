import pytest

from sqlalchemy.exc import IntegrityError

from src.models.parent_model import Parent

from src.support.repositories.parent_repository import ParentRepository
from src.support.repositories.highlighting_person_repository import HighlightingPersonRepository


@pytest.fixture
def highlighting_person_repository(session):
    return HighlightingPersonRepository(session)


@pytest.fixture
async def highlighting_person(
    highlighting_person_repository: HighlightingPersonRepository,
    parent
):
    await highlighting_person_repository.highlight_person(
        parent.parent_id,
        200001
    )

    return await (
        highlighting_person_repository.get_highlighting_person(
            parent.parent_id,
            200001
        )
    )


@pytest.mark.asyncio
async def test_highlight_person(
    highlighting_person_repository: HighlightingPersonRepository,
    parent
):
    await highlighting_person_repository.highlight_person(
        parent.parent_id,
        200001
    )

    result = await (
        highlighting_person_repository.get_highlighting_person(
            parent.parent_id,
            200001
        )
    )

    assert result is not None

    assert result.parent_id == parent.parent_id
    assert result.person_id == 200001


@pytest.mark.asyncio
async def test_highlight_person_duplicate_does_not_create_new(
    highlighting_person_repository: HighlightingPersonRepository,
    highlighting_person,
    parent
):
    await highlighting_person_repository.highlight_person(
        parent.parent_id,
        200001
    )

    result = await (
        highlighting_person_repository.get_highlighting_persons(
            parent.parent_id
        )
    )

    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_highlighting_person(
    highlighting_person_repository: HighlightingPersonRepository,
    highlighting_person,
    parent
):
    result = await (
        highlighting_person_repository.get_highlighting_person(
            parent.parent_id,
            200001
        )
    )

    assert result is not None

    assert result.parent_id == parent.parent_id
    assert result.person_id == 200001


@pytest.mark.asyncio
async def test_get_unknown_highlighting_person_returns_none(
    highlighting_person_repository: HighlightingPersonRepository,
    parent
):
    result = await (
        highlighting_person_repository.get_highlighting_person(
            parent.parent_id,
            999999
        )
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_highlighting_persons(
    highlighting_person_repository: HighlightingPersonRepository,
    parent
):
    await highlighting_person_repository.highlight_person(
        parent.parent_id,
        200001
    )

    await highlighting_person_repository.highlight_person(
        parent.parent_id,
        200002
    )

    result = await (
        highlighting_person_repository.get_highlighting_persons(
            parent.parent_id
        )
    )

    assert len(result) == 2


@pytest.mark.asyncio
async def test_unhighlight_person(
    highlighting_person_repository: HighlightingPersonRepository,
    highlighting_person,
    parent
):
    await highlighting_person_repository.unhighlight_person(
        parent.parent_id,
        200001
    )

    result = await (
        highlighting_person_repository.get_highlighting_person(
            parent.parent_id,
            200001
        )
    )

    assert result is None


@pytest.mark.asyncio
async def test_highlight_self_raises_error(
    highlighting_person_repository: HighlightingPersonRepository,
    parent
):
    with pytest.raises(IntegrityError):
        await highlighting_person_repository.highlight_person(
            parent.parent_id,
            parent.parent_id
        )


@pytest.mark.asyncio
async def test_highlight_unknown_parent_raises_error(
    highlighting_person_repository: HighlightingPersonRepository
):
    with pytest.raises(IntegrityError):
        await highlighting_person_repository.highlight_person(
            999999,
            200001
        )


@pytest.mark.asyncio
async def test_delete_parent_cascades_highlighting_persons(
    parent_repository: ParentRepository,
    highlighting_person_repository: HighlightingPersonRepository,
    highlighting_person,
    parent
):
    await parent_repository.delete(
        Parent.parent_id == parent.parent_id
    )

    result = await (
        highlighting_person_repository.get_highlighting_person(
            parent.parent_id,
            200001
        )
    )

    assert result is None
