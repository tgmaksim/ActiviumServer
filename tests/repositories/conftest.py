import pytest

from src.repositories.log_repository import LogRepository
from src.support.repositories.child_repository import ChildRepository
from src.support.repositories.review_repository import ReviewRepository
from src.support.repositories.parent_repository import ParentRepository
from src.support.repositories.session_repository import SessionRepository
from src.support.repositories.extracurricular_activity_repository import ExtracurricularActivityRepository


@pytest.fixture
def extracurricular_activity_repository(session):
    return ExtracurricularActivityRepository(session)


@pytest.fixture
def parent_repository(session):
    return ParentRepository(session)


@pytest.fixture
def child_repository(session):
    return ChildRepository(session)


@pytest.fixture
def session_repository(session):
    return SessionRepository(session)


@pytest.fixture
def review_repository(session):
    return ReviewRepository(session)


@pytest.fixture
def log_repository(session):
    return LogRepository(session)


@pytest.fixture
async def parent(
    parent_repository: ParentRepository
):
    return await parent_repository.create_parent(
        100001
    )


@pytest.fixture
async def child(
    child_repository: ChildRepository
):
    return await child_repository.create_child(
        child_id=100001,
        school_id=500,
        group_id=10,
        timezone=10800
    )


@pytest.fixture
async def auth_session(
    session_repository: SessionRepository,
    parent,
    child
):
    await session_repository.create_session(
        "session_1"
    )

    await session_repository.auth_session(
        session_id="session_1",
        dnevnik_token="token",
        parent_id=parent.parent_id,
        active_child_id=child.child_id
    )

    return await session_repository.get_session(
        "session_1"
    )


@pytest.fixture
async def review(
    review_repository: ReviewRepository,
    parent
):
    return await review_repository.create_review(
        parent_id=parent.parent_id,
        name="Maksim",
        stars=5,
        text="Excellent app",
        is_open=True
    )


@pytest.fixture
async def log(
    log_repository: LogRepository
):
    return await log_repository.add_log(
        ip="127.0.0.1",
        path="/api/test",
        session_id="session_1",
        status=True,
        method="GET",
        value="Success"
    )
