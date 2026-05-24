import pytest

from datetime import datetime, UTC

from .factories import (
    hour_factory,
    version_factory,
    tgbot_state_factory,
    extracurricular_activity_factory,
)

from src.support.repositories.hour_repository import HourRepository
from src.support.repositories.version_repository import VersionRepository
from src.support.repositories.tgbot_state_repository import TgbotStateRepository
from src.support.repositories.school_admin_repository import SchoolAdminRepository
from src.support.repositories.extracurricular_activity_repository import ExtracurricularActivityRepository
from src.support.repositories.ea_processing_notification_repository import EAProcessingNotificationRepository


@pytest.fixture
def version_repository(session):
    return VersionRepository(session)


@pytest.fixture
def tgbot_state_repository(session):
    return TgbotStateRepository(session)


@pytest.fixture
def hour_repository(session):
    return HourRepository(session)


@pytest.fixture
def school_admin_repository(session):
    return SchoolAdminRepository(session)


@pytest.fixture
def extracurricular_activity_repository(session):
    return ExtracurricularActivityRepository(session)


@pytest.fixture
def ea_processing_notification_repository(session):
    return EAProcessingNotificationRepository(session)


@pytest.fixture
async def versions(version_repository: VersionRepository):
    return await version_repository.create_many([
        version_factory(
            number=1,
            version="1.0.0",
            parent_version=None
        ),
        version_factory(
            number=2,
            version="1.0.1",
            parent_version=1
        )
    ])


@pytest.fixture
async def generic_version(version_repository: VersionRepository):
    return await version_repository.create(
        version_factory(
            number=1,
            version="1.0.0"
        )
    )


@pytest.fixture
async def tgbot_state(
    tgbot_state_repository: TgbotStateRepository
):
    state = tgbot_state_factory(
        key="123_456",
        state="waiting_message",
        data={
            "step": 1
        }
    )

    await tgbot_state_repository.set_state(
        state["key"],
        state["state"]
    )

    await tgbot_state_repository.set_data(
        state["key"],
        state["data"]
    )

    return await tgbot_state_repository.get_state(
        state["key"]
    )


@pytest.fixture
async def hour(
    hour_repository: HourRepository
):
    return await hour_repository.create(
        hour_factory(
            school_id=100
        )
    )


@pytest.fixture
async def school_hours(
    hour_repository: HourRepository
):
    return await hour_repository.create_many([
        hour_factory(
            school_id=100,
            months=[9, 10],
            weekdays=[1, 2, 3]
        ),
        hour_factory(
            school_id=100,
            months=[12],
            weekdays=[4, 5]
        ),
        hour_factory(
            school_id=200,
            months=[9],
            weekdays=[1]
        )
    ])


@pytest.fixture
async def school_admin(
    school_admin_repository: SchoolAdminRepository
):
    await school_admin_repository.create_admin(
        user_id=1,
        name="Main admin",
        parent_admin_id=None,
        person_id=100,
        school_id=500,
        timezone=0,
        dnevnik_token="token"
    )

    return await school_admin_repository.get_admin(1)


@pytest.fixture
async def child_school_admin(
    school_admin_repository: SchoolAdminRepository,
    school_admin
):
    await school_admin_repository.create_admin(
        user_id=2,
        name="Child admin",
        parent_admin_id=school_admin.user_id,
        person_id=None,
        school_id=None,
        timezone=None,
        dnevnik_token=None
    )

    return await school_admin_repository.get_admin(2)


@pytest.fixture
async def extracurricular_activities(
    extracurricular_activity_repository
):
    return await extracurricular_activity_repository.create_many([
        extracurricular_activity_factory(
            school_id=100,
            group_id=10,
            start_time=datetime(
                2025, 9, 1, 14, 0,
                tzinfo=UTC
            )
        ),
        extracurricular_activity_factory(
            school_id=100,
            group_id=10,
            start_time=datetime(
                2025, 9, 2, 14, 0,
                tzinfo=UTC
            )
        ),
        extracurricular_activity_factory(
            school_id=100,
            group_id=20,
            start_time=datetime(
                2025, 9, 1, 14, 0,
                tzinfo=UTC
            )
        ),
        extracurricular_activity_factory(
            school_id=200,
            group_id=10,
            start_time=datetime(
                2025, 9, 1, 14, 0,
                tzinfo=UTC
            )
        )
    ])


@pytest.fixture
async def ea_processing_notifications(
    extracurricular_activity_repository,
    ea_processing_notification_repository
):
    await extracurricular_activity_repository.create_many([
        extracurricular_activity_factory(
            school_id=100,
            group_id=1,
            start_time=datetime(
                2028, 1, 10, 14, 0,
                tzinfo=UTC
            )
        ),
        extracurricular_activity_factory(
            school_id=100,
            group_id=1,
            start_time=datetime(
                2028, 1, 10, 14, 0,
                tzinfo=UTC
            ),
            subject="Physics"
        ),
        extracurricular_activity_factory(
            school_id=100,
            group_id=1,
            start_time=datetime(
                2028, 1, 10, 15, 0,
                tzinfo=UTC
            )
        )
    ])

    return await ea_processing_notification_repository.get_multi()
