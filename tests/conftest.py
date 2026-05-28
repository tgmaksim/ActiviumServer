import pytest
import asyncio

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from src.config.project_config import settings  # Загрузка переменных окружения
from src.config.database.db_config import settings_db

from datetime import datetime, UTC, timedelta, date

from .factories import (
    hour_factory,
    version_factory,
    tgbot_state_factory,
    extracurricular_activity_factory,
)

from src.repositories.db_queue import AsyncDBQueue

from src.repositories.log_repository import LogRepository
from src.support.repositories.hour_repository import HourRepository
from src.support.repositories.child_repository import ChildRepository
from src.support.repositories.cache_repository import CacheRepository
from src.support.repositories.review_repository import ReviewRepository
from src.repositories.monitoring_repository import MonitoringRepository
from src.support.repositories.parent_repository import ParentRepository
from src.support.repositories.rating_repository import RatingRepository
from src.support.repositories.session_repository import SessionRepository
from src.support.repositories.version_repository import VersionRepository
from src.repositories.notification_repository import NotificationRepository
from src.support.repositories.referral_repository import ReferralRepository
from src.repositories.statistic_repository import StatisticRepository, StatName
from src.support.repositories.school_post_repository import SchoolPostRepository
from src.support.repositories.lesson_note_repository import LessonNoteRepository
from src.support.repositories.tgbot_state_repository import TgbotStateRepository
from src.support.repositories.review_likes_repository import ReviewLikeRepository
from src.support.repositories.information_repository import InformationRepository
from src.support.repositories.school_admin_repository import SchoolAdminRepository
from src.support.repositories.ea_notification_repository import EANotificationRepository
from src.support.repositories.marks_notification_repository import MarksNotificationRepository
from src.support.repositories.highlighting_person_repository import HighlightingPersonRepository
from src.support.repositories.extracurricular_activity_repository import ExtracurricularActivityRepository
from src.support.repositories.ea_processing_notification_repository import EAProcessingNotificationRepository


engine = create_async_engine(settings_db.database_url, echo=settings_db.DB_ECHO)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Создает один Event Loop на всю сессию тестирования"""

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    yield loop

    loop.close()


@pytest.fixture
async def session():
    async with engine.connect() as connection:
        transaction = await connection.begin()

        session = SessionLocal(bind=connection)
        db_queue = AsyncDBQueue(session)

        try:
            await db_queue.start()
            yield db_queue

        finally:
            await db_queue.stop()
            await session.close()
            await transaction.rollback()


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
def parent_repository(session):
    return ParentRepository(session)


@pytest.fixture
def child_repository(session):
    return ChildRepository(session)


@pytest.fixture
def session_repository(session):
    return SessionRepository(session)


@pytest.fixture
def cache_repository(session):
    return CacheRepository(session)


@pytest.fixture
def ea_notification_repository(session):
    return EANotificationRepository(session)


@pytest.fixture
def highlighting_person_repository(session):
    return HighlightingPersonRepository(session)


@pytest.fixture
def information_repository(session):
    return InformationRepository(session)


@pytest.fixture
def lesson_note_repository(session):
    return LessonNoteRepository(session)


@pytest.fixture
def marks_notification_repository(session):
    return MarksNotificationRepository(session)


@pytest.fixture
def rating_repository(session):
    return RatingRepository(session)


@pytest.fixture
def referral_repository(session):
    return ReferralRepository(session)


@pytest.fixture
def review_repository(session):
    return ReviewRepository(session)


@pytest.fixture
def review_like_repository(session):
    return ReviewLikeRepository(session)


@pytest.fixture
def school_post_repository(session):
    return SchoolPostRepository(session)


@pytest.fixture
def log_repository(session):
    return LogRepository(session)


@pytest.fixture
def notification_repository(session):
    return NotificationRepository(session)


@pytest.fixture
def monitoring_repository(session):
    return MonitoringRepository(session)


@pytest.fixture
def statistic_repository(session):
    return StatisticRepository(session)


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
    extracurricular_activity_repository: ExtracurricularActivityRepository,
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
    extracurricular_activity_repository: ExtracurricularActivityRepository,
    ea_processing_notification_repository: EAProcessingNotificationRepository,
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
async def app_session(
    session_repository: SessionRepository
):
    await session_repository.create_session(
        "session_1"
    )

    return await session_repository.get_session(
        "session_1",
        only_life=False
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
async def caches(
    cache_repository: CacheRepository,
    auth_session,
    child
):
    return await cache_repository.put_caches(
        auth_session.session_id,
        child.child_id,
        [
            ("profile", {"name": "Maksim"}),
            ("lessons", [{"lesson": 1}])
        ]
    )


@pytest.fixture
async def ea_notification(
    ea_notification_repository: EANotificationRepository,
    auth_session,
    child
):
    return await ea_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )


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


@pytest.fixture
async def lesson_note(
    lesson_note_repository: LessonNoteRepository,
    child
):
    return await lesson_note_repository.create_note(
        child_id=child.child_id,
        lesson_id=1000,
        text="Test note",
        public=True,
        remind_time=datetime(
            2028, 1, 10, 12, 0,
            tzinfo=UTC
        )
    )


@pytest.fixture
async def lesson_notes(
    lesson_note_repository: LessonNoteRepository,
    child
):
    return [
        await lesson_note_repository.create_note(
            child_id=child.child_id,
            lesson_id=1000,
            text="Public note",
            public=True,
            remind_time=datetime(
                2028, 1, 10, 12, 0,
                tzinfo=UTC
            )
        ),

        await lesson_note_repository.create_note(
            child_id=child.child_id,
            lesson_id=1001,
            text="Private note",
            public=False,
            remind_time=None
        ),

        await lesson_note_repository.create_note(
            child_id=child.child_id,
            lesson_id=1002,
            text="Second public note",
            public=True,
            remind_time=datetime(
                2028, 1, 10, 13, 0,
                tzinfo=UTC
            )
        )
    ]


@pytest.fixture
async def marks_notification(
    marks_notification_repository: MarksNotificationRepository,
    auth_session,
    child
):
    await marks_notification_repository.turn_on(
        auth_session.session_id,
        child.child_id
    )

    return await marks_notification_repository.get_status(
        auth_session.session_id,
        child.child_id
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


@pytest.fixture
async def notifications(
    log_repository: LogRepository,
    notification_repository: NotificationRepository
):
    await log_repository.add_log(
        ip="127.0.0.1",
        path="/api/1",
        session_id="session_1",
        status=True,
        method="GET",
        value="success"
    )

    await log_repository.add_log(
        ip="127.0.0.1",
        path="/api/2",
        session_id="session_2",
        status=False,
        method="POST",
        value="error"
    )

    await log_repository.add_log(
        ip="127.0.0.1",
        path="/api/3",
        session_id="session_3",
        status=True,
        method="DELETE",
        value="success 2"
    )

    return await notification_repository.get_multi()


@pytest.fixture
async def monitoring(
    monitoring_repository: MonitoringRepository
):
    await monitoring_repository.add_monitoring(
        path="/api/test",
        session_id="session_1",
        status=True,
        duration=timedelta(milliseconds=250)
    )

    return await monitoring_repository.get_single(path="/api/test")


@pytest.fixture
async def monitorings(
    monitoring_repository: MonitoringRepository
):
    await monitoring_repository.add_monitoring(
        path="/api/users",
        session_id="session_1",
        status=True,
        duration=timedelta(milliseconds=100)
    )

    await monitoring_repository.add_monitoring(
        path="/api/users",
        session_id="session_2",
        status=True,
        duration=timedelta(milliseconds=300)
    )

    await monitoring_repository.add_monitoring(
        path="/api/users",
        session_id="session_3",
        status=False,
        duration=timedelta(milliseconds=500)
    )

    await monitoring_repository.add_monitoring(
        path="/api/posts",
        session_id="session_4",
        status=True,
        duration=timedelta(milliseconds=200)
    )

    return await monitoring_repository.get_multi()


@pytest.fixture
async def statistic(
    statistic_repository: StatisticRepository
):
    await statistic_repository.add_statistic(
        parent_id=100001,
        key=StatName.getMarks
    )

    return await statistic_repository.get_single(parent_id=100001)


@pytest.fixture
async def statistics(
    statistic_repository: StatisticRepository
):
    await statistic_repository.add_statistic(
        parent_id=100001,
        key=StatName.getMarks
    )

    await statistic_repository.add_statistic(
        parent_id=100001,
        key=StatName.getSchedule
    )

    await statistic_repository.add_statistic(
        parent_id=100002,
        key=StatName.getMarks
    )

    await statistic_repository.add_statistic(
        parent_id=None,
        key="custom_event"
    )

    return await statistic_repository.get_multi()
