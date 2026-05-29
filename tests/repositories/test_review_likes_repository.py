import pytest

from sqlalchemy.exc import IntegrityError

from src.models.review_like_model import ReviewLike

from src.support.repositories.parent_repository import ParentRepository
from src.support.repositories.review_repository import ReviewRepository
from src.support.repositories.review_likes_repository import ReviewLikeRepository


@pytest.fixture
def review_like_repository(session):
    return ReviewLikeRepository(session)


@pytest.fixture
async def second_parent(
    parent_repository: ParentRepository
):
    return await parent_repository.create_parent(
        100002
    )


@pytest.fixture
async def second_review(
    review_repository: ReviewRepository,
    second_parent
):
    return await review_repository.create_review(
        parent_id=second_parent.parent_id,
        name="Alex",
        stars=4,
        text="Good app",
        is_open=True
    )


@pytest.fixture
async def review_like(
    review_like_repository: ReviewLikeRepository,
    parent,
    second_review
):
    return await review_like_repository.like_review(
        parent_id=parent.parent_id,
        review_id=second_review.parent_id
    )


@pytest.fixture
async def review_likes(
    review_like_repository: ReviewLikeRepository,
    parent,
    second_parent,
    review,
    second_review
):
    await review_like_repository.like_review(
        parent_id=parent.parent_id,
        review_id=second_review.parent_id
    )

    await review_like_repository.like_review(
        parent_id=second_parent.parent_id,
        review_id=review.parent_id
    )

    return [
        await review_like_repository.get_like(
            parent.parent_id,
            second_review.parent_id
        ),
        await review_like_repository.get_like(
            second_parent.parent_id,
            review.parent_id
        )
    ]


@pytest.mark.asyncio
async def test_like_review(
    review_like_repository: ReviewLikeRepository,
    parent,
    second_review
):
    review_like = await review_like_repository.like_review(
        parent_id=parent.parent_id,
        review_id=second_review.parent_id
    )

    assert isinstance(review_like, ReviewLike)

    assert review_like.parent_id == parent.parent_id
    assert review_like.review_id == second_review.parent_id


@pytest.mark.asyncio
async def test_get_like(
    review_like_repository: ReviewLikeRepository,
    review_like
):
    result = await review_like_repository.get_like(
        review_like.parent_id,
        review_like.review_id
    )

    assert result is not None

    assert result.parent_id == review_like.parent_id
    assert result.review_id == review_like.review_id


@pytest.mark.asyncio
async def test_has_my_likes(
    review_like_repository: ReviewLikeRepository,
    review_likes,
    parent,
    review,
    second_review
):
    result = await review_like_repository.has_my_likes(
        parent.parent_id,
        [
            review.parent_id,
            second_review.parent_id
        ]
    )

    assert result == {
        second_review.parent_id
    }


@pytest.mark.asyncio
async def test_delete_like(
    review_like_repository: ReviewLikeRepository,
    review_like
):
    await review_like_repository.delete_like(
        review_like.parent_id,
        review_like.review_id
    )

    result = await review_like_repository.get_like(
        review_like.parent_id,
        review_like.review_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_like_review_duplicate_pk(
    review_like_repository: ReviewLikeRepository,
    review_like
):
    with pytest.raises(IntegrityError):
        await review_like_repository.like_review(
            parent_id=review_like.parent_id,
            review_id=review_like.review_id
        )


@pytest.mark.asyncio
async def test_like_review_invalid_parent_fk(
    review_like_repository: ReviewLikeRepository,
    second_review
):
    with pytest.raises(IntegrityError):
        await review_like_repository.like_review(
            parent_id=999999,
            review_id=second_review.parent_id
        )


@pytest.mark.asyncio
async def test_like_review_invalid_review_fk(
    review_like_repository: ReviewLikeRepository,
    parent
):
    with pytest.raises(IntegrityError):
        await review_like_repository.like_review(
            parent_id=parent.parent_id,
            review_id=999999
        )


@pytest.mark.asyncio
async def test_delete_parent_cascade_review_like(
    review_like_repository: ReviewLikeRepository,
    parent_repository: ParentRepository,
    review_like
):
    await parent_repository.delete(
        parent_repository.model.parent_id == review_like.parent_id
    )

    result = await review_like_repository.get_like(
        review_like.parent_id,
        review_like.review_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_review_cascade_review_like(
    review_like_repository: ReviewLikeRepository,
    review_repository: ReviewRepository,
    review_like
):
    await review_repository.delete_review(
        review_like.review_id
    )

    result = await review_like_repository.get_like(
        review_like.parent_id,
        review_like.review_id
    )

    assert result is None
