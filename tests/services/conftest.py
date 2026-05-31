import pytest

from types import SimpleNamespace

from unittest.mock import AsyncMock


class FakeUoW:
    def __init__(self):
        self.log_repository = AsyncMock()
        self.version_repository = AsyncMock()
        self.statistic_repository = AsyncMock()
        self.session_repository = AsyncMock()
        self.hour_repository = AsyncMock()
        self.child_repository = AsyncMock()
        self.parent_repository = AsyncMock()
        self.cache_repository = AsyncMock()
        self.extracurricular_activity_repository = AsyncMock()
        self.rating_repository = AsyncMock()
        self.marks_notification_repository = AsyncMock()
        self.review_repository = AsyncMock()
        self.review_like_repository = AsyncMock()
        self.lesson_note_repository = AsyncMock()
        self.ea_notification_repository = AsyncMock()
        self.ea_processing_notification_repository = AsyncMock()
        self.highlighting_person_repository = AsyncMock()
        self.information_repository = AsyncMock()
        self.referral_repository = AsyncMock()
        self.school_admin_repository = AsyncMock()
        self.school_post_repository = AsyncMock()
        self.tgbot_state_repository = AsyncMock()
        self.school_post_vision_repository = AsyncMock()
        self.school_post_click_repository = AsyncMock()
        self.school_post_viewing_repository = AsyncMock()
        self.school_post_like_repository = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.fixture
def fake_uow():
    return FakeUoW()


@pytest.fixture
def uow_factory(fake_uow):
    return lambda: fake_uow


@pytest.fixture
def fake_session():
    return SimpleNamespace(
        session_id="session_1",
        parent_id=100001,
        active_child_id=200001
    )


@pytest.fixture
def generic_latest_version():
    return SimpleNamespace(
        number=200,
        version="2.0.0",
        status_id=0.5,
        status="recommended",
        info="Generic update",
        logs="Generic logs",
        date="01.01.2025"
    )


@pytest.fixture
def latest_version():
    return SimpleNamespace(
        number=203,
        version="2.0.3",
        status_id=0.5,
        status="recommended",
        info="Latest update",
        logs="Latest logs",
        date="04.01.2025"
    )


@pytest.fixture
def mini_versions():
    return [
        SimpleNamespace(number=201, logs="Mini 1"),
        SimpleNamespace(number=202, logs="Mini 2"),
        SimpleNamespace(number=203, logs="Mini 3"),
    ]


@pytest.fixture
def important_version():
    return SimpleNamespace(
        status_id=1,
        status="critical",
        info="important info"
    )


@pytest.fixture
def fake_parent():
    return SimpleNamespace(
        parent_id=100001
    )


@pytest.fixture
def fake_child():
    return SimpleNamespace(
        child_id=200001,
        school_id=1,
        group_id=2,
        timezone=10800
    )


@pytest.fixture
def mock_dnr():
    dnr = AsyncMock()

    dnr.get_context = AsyncMock()
    dnr.get_info = AsyncMock()
    dnr.get_children = AsyncMock()
    dnr.get_user_info = AsyncMock()

    return dnr
