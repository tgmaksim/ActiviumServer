import pytest

from datetime import datetime, timedelta, UTC

from sqlalchemy.exc import IntegrityError

from src.models.parent_model import Parent

from src.support.repositories.parent_repository import ParentRepository
from src.support.repositories.information_repository import InformationRepository


@pytest.fixture
def information_repository(session):
    return InformationRepository(session)


@pytest.fixture
async def information(
    information_repository: InformationRepository,
    parent
):
    time = datetime.now(UTC) - timedelta(hours=1)

    return await information_repository.create_information(
        parent_id=parent.parent_id,
        type_="warning",
        time=time,
        title="Test title",
        text="Test text"
    )


@pytest.fixture
async def future_information(
    information_repository: InformationRepository,
    parent
):
    time = datetime.now(UTC) + timedelta(days=1)

    return await information_repository.create_information(
        parent_id=parent.parent_id,
        type_="future",
        time=time,
        title="Future title",
        text="Future text"
    )


@pytest.mark.asyncio
async def test_create_information(
    information_repository: InformationRepository,
    parent
):
    time = datetime.now(UTC)

    result = await information_repository.create_information(
        parent_id=parent.parent_id,
        type_="warning",
        time=time,
        title="Important",
        text="Some text"
    )

    assert result is not None

    assert result.parent_id == parent.parent_id
    assert result.type == "warning"
    assert result.title == "Important"
    assert result.text == "Some text"
    assert result.time == time


@pytest.mark.asyncio
async def test_get_informations_returns_only_past(
    information_repository: InformationRepository,
    information,
    future_information,
    parent
):
    result = await information_repository.get_informations(
        parent.parent_id
    )

    assert len(result) == 1

    assert result[0].type == "warning"


@pytest.mark.asyncio
async def test_get_informations_returns_empty(
    information_repository: InformationRepository,
    parent
):
    result = await information_repository.get_informations(
        parent.parent_id
    )

    assert result == []


@pytest.mark.asyncio
async def test_delete_informations(
    information_repository: InformationRepository,
    information,
    future_information,
    parent
):
    await information_repository.delete_informations(
        parent.parent_id
    )

    result = await information_repository.get_multi()

    assert len(result) == 1

    assert result[0].type == "future"


@pytest.mark.asyncio
async def test_create_duplicate_information_raises_error(
    information_repository: InformationRepository,
    information,
    parent
):
    with pytest.raises(IntegrityError):
        await information_repository.create_information(
            parent_id=parent.parent_id,
            type_=information.type,
            time=information.time,
            title="Duplicate",
            text="Duplicate"
        )


@pytest.mark.asyncio
async def test_create_information_unknown_parent_raises_error(
    information_repository: InformationRepository
):
    with pytest.raises(IntegrityError):
        await information_repository.create_information(
            parent_id=999999,
            type_="warning",
            time=datetime.now(UTC),
            title="Title",
            text="Text"
        )


@pytest.mark.asyncio
async def test_delete_parent_cascades_information(
    parent_repository: ParentRepository,
    information_repository: InformationRepository,
    information,
    parent
):
    await parent_repository.delete(
        Parent.parent_id == parent.parent_id
    )

    result = await information_repository.get_multi()

    assert result == []
