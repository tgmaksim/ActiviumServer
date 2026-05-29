import pytest

from sqlalchemy.exc import IntegrityError

from src.models.review_model import Review
from src.support.repositories.review_repository import ReviewRepository
from src.support.repositories.parent_repository import ParentRepository


@pytest.fixture
async def reviews(
    review_repository: ReviewRepository,
    parent_repository: ParentRepository,
    parent
):
    await parent_repository.create_parent(100002)
    await parent_repository.create_parent(100003)

    await review_repository.create_review(
        parent_id=100001,
        name="Maksim",
        stars=5,
        text="Best",
        is_open=True
    )

    await review_repository.create_review(
        parent_id=100002,
        name="Alex",
        stars=3,
        text="Normal",
        is_open=True
    )

    await review_repository.create_review(
        parent_id=100003,
        name="Ivan",
        stars=1,
        text="Bad",
        is_open=True
    )

    await review_repository.like_review(100001)
    await review_repository.like_review(100001)

    await review_repository.like_review(100002)

    return [
        await review_repository.get_review(100001),
        await review_repository.get_review(100002),
        await review_repository.get_review(100003)
    ]


@pytest.mark.asyncio
async def test_create_review(
    review_repository: ReviewRepository,
    parent
):
    review = await review_repository.create_review(
        parent_id=parent.parent_id,
        name="Maksim",
        stars=5,
        text="Excellent app"
    )

    assert isinstance(review, Review)

    assert review.parent_id == parent.parent_id
    assert review.name == "Maksim"
    assert review.stars == 5
    assert review.text == "Excellent app"

    assert review.likes == 0
    assert review.is_updated is False
    assert review.is_open is False


@pytest.mark.asyncio
async def test_create_review_invalid_stars(
    review_repository: ReviewRepository,
    parent
):
    with pytest.raises(IntegrityError):
        await review_repository.create_review(
            parent_id=parent.parent_id,
            name="Maksim",
            stars=6,
            text="Invalid"
        )


@pytest.mark.asyncio
async def test_create_review_duplicate_pk(
    review_repository: ReviewRepository,
    review
):
    with pytest.raises(IntegrityError):
        await review_repository.create_review(
            parent_id=review.parent_id,
            name="Duplicate",
            stars=4,
            text="Duplicate"
        )


@pytest.mark.asyncio
async def test_get_review(
    review_repository: ReviewRepository,
    review
):
    result = await review_repository.get_review(
        review.parent_id
    )

    assert result is not None
    assert result.parent_id == review.parent_id


@pytest.mark.asyncio
async def test_get_review_only_is_open(
    review_repository: ReviewRepository,
    parent
):
    await review_repository.create_review(
        parent_id=parent.parent_id,
        name="Closed",
        stars=5,
        text="Hidden",
        is_open=False
    )

    result = await review_repository.get_review(
        parent.parent_id,
        only_is_open=True
    )

    assert result is None


@pytest.mark.asyncio
async def test_open_review(
    review_repository: ReviewRepository,
    parent
):
    await review_repository.create_review(
        parent_id=parent.parent_id,
        name="Maksim",
        stars=5,
        text="Review"
    )

    result = await review_repository.open_review(
        parent.parent_id
    )

    assert result.is_open is True


@pytest.mark.asyncio
async def test_update_review(
    review_repository: ReviewRepository,
    review
):
    result = await review_repository.update_review(
        parent_id=review.parent_id,
        name="Updated",
        stars=2,
        text="Updated text"
    )

    assert result.name == "Updated"
    assert result.stars == 2
    assert result.text == "Updated text"

    assert result.is_updated is True
    assert result.is_open is False


@pytest.mark.asyncio
async def test_delete_review(
    review_repository: ReviewRepository,
    review
):
    await review_repository.delete_review(
        review.parent_id
    )

    result = await review_repository.get_review(
        review.parent_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_reviews_by_likes(
    review_repository: ReviewRepository,
    reviews
):
    result = await review_repository.get_reviews_by_likes(
        offset=0,
        limit=10
    )

    assert len(result) == 3

    assert result[0].likes == 2
    assert result[1].likes == 1
    assert result[2].likes == 0


@pytest.mark.asyncio
async def test_get_reviews_by_max_stars(
    review_repository: ReviewRepository,
    reviews
):
    result = await review_repository.get_reviews_by_max_stars(
        offset=0,
        limit=10
    )

    assert len(result) == 3

    assert result[0].stars == 5
    assert result[1].stars == 3
    assert result[2].stars == 1


@pytest.mark.asyncio
async def test_get_reviews_by_min_stars(
    review_repository: ReviewRepository,
    reviews
):
    result = await review_repository.get_reviews_by_min_stars(
        offset=0,
        limit=10
    )

    assert len(result) == 3

    assert result[0].stars == 1
    assert result[1].stars == 3
    assert result[2].stars == 5


@pytest.mark.asyncio
async def test_like_review(
    review_repository: ReviewRepository,
    review
):
    old_likes = review.likes

    result = await review_repository.like_review(
        review.parent_id
    )

    assert result.likes == old_likes + 1


@pytest.mark.asyncio
async def test_delete_like(
    review_repository: ReviewRepository,
    review
):
    await review_repository.like_review(
        review.parent_id
    )

    result = await review_repository.delete_like(
        review.parent_id
    )

    assert result.likes == 0


@pytest.mark.asyncio
async def test_delete_like_invalid_check_constraint(
    review_repository: ReviewRepository,
    review
):
    with pytest.raises(IntegrityError):
        await review_repository.delete_like(
            review.parent_id
        )


@pytest.mark.asyncio
async def test_delete_parent_cascade_review(
    review_repository: ReviewRepository,
    parent_repository: ParentRepository,
    review
):
    await parent_repository.delete(
        parent_repository.model.parent_id == review.parent_id
    )

    result = await review_repository.get_review(
        review.parent_id
    )

    assert result is None