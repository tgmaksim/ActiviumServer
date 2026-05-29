import pytest

from datetime import date

from sqlalchemy.exc import IntegrityError

from src.support.repositories.school_post_repository import SchoolPostRepository


@pytest.fixture
def school_post_repository(session):
    return SchoolPostRepository(session)


@pytest.fixture
async def school_post(
    school_post_repository: SchoolPostRepository
):
    return await school_post_repository.create_post(
        school_id=100,
        timezone=10800,
        title="School event",
        description="Description",
        has_image=True,
        author="Admin",
        schedule_date=date(2025, 9, 10),
        content=[
            {
                "type": "text",
                "text": "Hello",
                "entities": []
            }
        ]
    )


@pytest.fixture
async def school_posts(
    school_post_repository: SchoolPostRepository
):
    return [
        await school_post_repository.create_post(
            school_id=100,
            timezone=10800,
            title="School post",
            description=None,
            has_image=False,
            author="Admin",
            schedule_date=date(2025, 9, 10),
            content=[]
        ),
        await school_post_repository.create_post(
            school_id=None,
            timezone=0,
            title="Global post",
            description=None,
            has_image=False,
            author="System",
            schedule_date=date(2025, 9, 15),
            content=[]
        ),
        await school_post_repository.create_post(
            school_id=200,
            timezone=7200,
            title="Other school",
            description=None,
            has_image=False,
            author="Other",
            schedule_date=date(2025, 10, 1),
            content=[]
        )
    ]


@pytest.mark.asyncio
async def test_create_post(
    school_post
):
    assert school_post.post_id is not None
    assert school_post.school_id == 100
    assert school_post.timezone == 10800
    assert school_post.title == "School event"
    assert school_post.description == "Description"
    assert school_post.has_image is True
    assert school_post.author == "Admin"


@pytest.mark.asyncio
async def test_get_post(
    school_post_repository: SchoolPostRepository,
    school_post
):
    post = await school_post_repository.get_post(
        school_post.post_id
    )

    assert post is not None
    assert post.post_id == school_post.post_id


@pytest.mark.asyncio
async def test_get_post_not_found(
    school_post_repository: SchoolPostRepository
):
    post = await school_post_repository.get_post(999999)

    assert post is None


@pytest.mark.asyncio
async def test_get_admin_school_posts(
    school_post_repository: SchoolPostRepository,
    school_posts
):
    posts = await school_post_repository.get_admin_school_posts(
        100
    )

    assert len(posts) == 1
    assert posts[0].school_id == 100


async def test_get_school_posts(
    school_post_repository: SchoolPostRepository,
    school_posts
):
    posts = await school_post_repository.get_school_posts(
        100
    )

    posts_id = {post.post_id for post in posts}

    assert len(posts) == 2
    assert school_posts[0].post_id in posts_id
    assert school_posts[1].post_id in posts_id


@pytest.mark.asyncio
async def test_get_school_posts_limit(
    school_post_repository: SchoolPostRepository,
    school_posts
):
    posts = await school_post_repository.get_school_posts(
        100,
        limit=1
    )

    assert len(posts) == 1


async def test_get_schedule_posts(
    school_post_repository: SchoolPostRepository,
    school_posts
):
    posts = await school_post_repository.get_schedule_posts(
        100,
        start=date(2025, 9, 1),
        end=date(2025, 9, 30)
    )

    posts_id = {post.post_id for post in posts}

    assert len(posts) == 2
    assert school_posts[0].post_id in posts_id
    assert school_posts[1].post_id in posts_id


@pytest.mark.asyncio
async def test_delete_post(
    school_post_repository: SchoolPostRepository,
    school_post
):
    await school_post_repository.delete_post(
        school_post.post_id
    )

    deleted = await school_post_repository.get_post(
        school_post.post_id
    )

    assert deleted is None


@pytest.mark.asyncio
async def test_see_post(
    school_post_repository: SchoolPostRepository,
    school_post
):
    updated = await school_post_repository.see_post(
        school_post.post_id
    )

    assert updated.count_visions == 1


@pytest.mark.asyncio
async def test_click_post(
    school_post_repository: SchoolPostRepository,
    school_post
):
    updated = await school_post_repository.click_post(
        school_post.post_id
    )

    assert updated.count_clicks == 1


@pytest.mark.asyncio
async def test_view_post(
    school_post_repository: SchoolPostRepository,
    school_post
):
    updated = await school_post_repository.view_post(
        school_post.post_id
    )

    assert updated.count_viewings == 1


@pytest.mark.asyncio
async def test_like_post(
    school_post_repository: SchoolPostRepository,
    school_post
):
    updated = await school_post_repository.like_post(
        school_post.post_id
    )

    assert updated.count_likes == 1


@pytest.mark.asyncio
async def test_unlike_post(
    school_post_repository: SchoolPostRepository,
    school_post
):
    await school_post_repository.like_post(
        school_post.post_id
    )

    updated = await school_post_repository.unlike_post(
        school_post.post_id
    )

    assert updated.count_likes == 0


@pytest.mark.asyncio
async def test_unlike_post_below_zero(
    school_post_repository: SchoolPostRepository,
    school_post
):
    with pytest.raises(IntegrityError):
        await school_post_repository.unlike_post(
            school_post.post_id
        )
