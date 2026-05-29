import pytest

from sqlalchemy.exc import IntegrityError

from src.support.repositories.rating_repository import RatingRepository


@pytest.fixture
def rating_repository(session):
    return RatingRepository(session)


@pytest.mark.asyncio
async def test_put_rating(
    rating_repository: RatingRepository,
    child
):
    result = await rating_repository.put_rating(
        child_id=child.child_id,
        period_id=1,
        subject_id=2,
        number=3,
        avg="4.75",
        mood="good"
    )

    assert result is not None

    assert result.child_id == child.child_id
    assert result.period_id == 1
    assert result.subject_id == 2

    assert result.number == 3
    assert result.avg == "4.75"
    assert result.mood == "good"


@pytest.mark.asyncio
async def test_put_rating_updates_existing(
    rating_repository: RatingRepository,
    child
):
    await rating_repository.put_rating(
        child_id=child.child_id,
        period_id=1,
        subject_id=2,
        number=3,
        avg="4.75",
        mood="good"
    )

    result = await rating_repository.put_rating(
        child_id=child.child_id,
        period_id=1,
        subject_id=2,
        number=1,
        avg="5",
        mood="more"
    )

    assert result is not None

    assert result.number == 1
    assert result.avg == "5"
    assert result.mood == "more"


@pytest.mark.asyncio
async def test_get_rating(
    rating_repository: RatingRepository,
    child
):
    await rating_repository.put_rating(
        child_id=child.child_id,
        period_id=1,
        subject_id=2,
        number=3,
        avg="4.75",
        mood="good"
    )

    result = await rating_repository.get_rating(
        child.child_id,
        1,
        2
    )

    assert result is not None

    assert result.child_id == child.child_id
    assert result.period_id == 1
    assert result.subject_id == 2


@pytest.mark.asyncio
async def test_get_unknown_rating_returns_none(
    rating_repository: RatingRepository
):
    result = await rating_repository.get_rating(
        999,
        999,
        999
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_rating(
    rating_repository: RatingRepository,
    child
):
    await rating_repository.put_rating(
        child_id=child.child_id,
        period_id=1,
        subject_id=2,
        number=3,
        avg="4.75",
        mood="good"
    )

    await rating_repository.delete_rating(
        child.child_id,
        1,
        2
    )

    result = await rating_repository.get_rating(
        child.child_id,
        1,
        2
    )

    assert result is None


@pytest.mark.asyncio
async def test_put_rating_with_unknown_child_raises(
    rating_repository: RatingRepository
):
    with pytest.raises(IntegrityError):
        await rating_repository.put_rating(
            child_id=999999,
            period_id=1,
            subject_id=2,
            number=3,
            avg="4.75",
            mood="good"
        )
