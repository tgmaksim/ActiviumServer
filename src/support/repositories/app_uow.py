from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .ad_repository import AdRepository
from .hour_repository import HourRepository
from .child_repository import ChildRepository
from .cache_repository import CacheRepository
from .review_repository import ReviewRepository
from .parent_repository import ParentRepository
from .rating_repository import RatingRepository
from .session_repository import SessionRepository
from .version_repository import VersionRepository
from .referral_repository import ReferralRepository
from .ad_viewing_repository import AdViewingRepository
from .tgbot_state_repository import TgbotStateRepository
from .school_post_repository import SchoolPostRepository
from .lesson_note_repository import LessonNoteRepository
from ...repositories.log_repository import LogRepository
from .review_likes_repository import ReviewLikeRepository
from .information_repository import InformationRepository
from .school_admin_repository import SchoolAdminRepository
from .ea_notification_repository import EANotificationRepository
from .school_post_like_repository import SchoolPostLikeRepository
from .school_post_click_repository import SchoolPostClickRepository
from ...repositories.statistic_repository import StatisticRepository
from .school_post_vision_repository import SchoolPostVisionRepository
from .marks_notification_repository import MarksNotificationRepository
from .school_post_viewing_repository import SchoolPostViewingRepository
from .highlighting_person_repository import HighlightingPersonRepository
from .extracurricular_activity_repository import ExtracurricularActivityRepository
from .ea_processing_notification_repository import EAProcessingNotificationRepository

from ...repositories.sqlalchemy_uow import SqlAlchemyUnitOfWork


__all__ = ['AppUnitOfWork']


class AppUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory)

        self._log_repository: Optional[LogRepository] = None
        self._version_repository: Optional[VersionRepository] = None
        self._statistic_repository: Optional[StatisticRepository] = None
        self._session_repository: Optional[SessionRepository] = None
        self._hour_repository: Optional[HourRepository] = None
        self._child_repository: Optional[ChildRepository] = None
        self._parent_repository: Optional[ParentRepository] = None
        self._cache_repository: Optional[CacheRepository] = None
        self._extracurricular_activity_repository: Optional[ExtracurricularActivityRepository] = None
        self._rating_repository: Optional[RatingRepository] = None
        self._marks_notification_repository: Optional[MarksNotificationRepository] = None
        self._review_repository: Optional[ReviewRepository] = None
        self._review_like_repository: Optional[ReviewLikeRepository] = None
        self._lesson_note_repository: Optional[LessonNoteRepository] = None
        self._ea_notification_repository: Optional[EANotificationRepository] = None
        self._ea_processing_notification_repository: Optional[EAProcessingNotificationRepository] = None
        self._highlighting_person_repository: Optional[HighlightingPersonRepository] = None
        self._information_repository: Optional[InformationRepository] = None
        self._referral_repository: Optional[ReferralRepository] = None
        self._school_admin_repository: Optional[SchoolAdminRepository] = None
        self._school_post_repository: Optional[SchoolPostRepository] = None
        self._tgbot_state_repository: Optional[TgbotStateRepository] = None
        self._school_post_vision_repository: Optional[SchoolPostVisionRepository] = None
        self._school_post_click_repository: Optional[SchoolPostClickRepository] = None
        self._school_post_viewing_repository: Optional[SchoolPostViewingRepository] = None
        self._school_post_like_repository: Optional[SchoolPostLikeRepository] = None
        self._ad_repository: Optional[AdRepository] = None
        self._ad_viewing_repository: Optional[AdViewingRepository] = None

    @property
    def log_repository(self) -> LogRepository:
        if self._log_repository is None:
            self._log_repository = LogRepository(self.queue)
        return self._log_repository

    @property
    def version_repository(self) -> VersionRepository:
        if self._version_repository is None:
            self._version_repository = VersionRepository(self.queue)
        return self._version_repository

    @property
    def statistic_repository(self) -> StatisticRepository:
        if self._statistic_repository is None:
            self._statistic_repository = StatisticRepository(self.queue)
        return self._statistic_repository

    @property
    def session_repository(self) -> SessionRepository:
        if self._session_repository is None:
            self._session_repository = SessionRepository(self.queue)
        return self._session_repository

    @property
    def hour_repository(self) -> HourRepository:
        if self._hour_repository is None:
            self._hour_repository = HourRepository(self.queue)
        return self._hour_repository

    @property
    def child_repository(self) -> ChildRepository:
        if self._child_repository is None:
            self._child_repository = ChildRepository(self.queue)
        return self._child_repository

    @property
    def parent_repository(self) -> ParentRepository:
        if self._parent_repository is None:
            self._parent_repository = ParentRepository(self.queue)
        return self._parent_repository

    @property
    def cache_repository(self) -> CacheRepository:
        if self._cache_repository is None:
            self._cache_repository = CacheRepository(self.queue)
        return self._cache_repository

    @property
    def extracurricular_activity_repository(self) -> ExtracurricularActivityRepository:
        if self._extracurricular_activity_repository is None:
            self._extracurricular_activity_repository = ExtracurricularActivityRepository(self.queue)
        return self._extracurricular_activity_repository

    @property
    def rating_repository(self) -> RatingRepository:
        if self._rating_repository is None:
            self._rating_repository = RatingRepository(self.queue)
        return self._rating_repository

    @property
    def marks_notification_repository(self) -> MarksNotificationRepository:
        if self._marks_notification_repository is None:
            self._marks_notification_repository = MarksNotificationRepository(self.queue)
        return self._marks_notification_repository

    @property
    def review_repository(self) -> ReviewRepository:
        if self._review_repository is None:
            self._review_repository = ReviewRepository(self.queue)
        return self._review_repository

    @property
    def review_like_repository(self) -> ReviewLikeRepository:
        if self._review_like_repository is None:
            self._review_like_repository = ReviewLikeRepository(self.queue)
        return self._review_like_repository

    @property
    def lesson_note_repository(self) -> LessonNoteRepository:
        if self._lesson_note_repository is None:
            self._lesson_note_repository = LessonNoteRepository(self.queue)
        return self._lesson_note_repository

    @property
    def ea_notification_repository(self) -> EANotificationRepository:
        if self._ea_notification_repository is None:
            self._ea_notification_repository = EANotificationRepository(self.queue)
        return self._ea_notification_repository

    @property
    def ea_processing_notification_repository(self) -> EAProcessingNotificationRepository:
        if self._ea_processing_notification_repository is None:
            self._ea_processing_notification_repository = EAProcessingNotificationRepository(self.queue)
        return self._ea_processing_notification_repository

    @property
    def highlighting_person_repository(self) -> HighlightingPersonRepository:
        if self._highlighting_person_repository is None:
            self._highlighting_person_repository = HighlightingPersonRepository(self.queue)
        return self._highlighting_person_repository

    @property
    def information_repository(self) -> InformationRepository:
        if self._information_repository is None:
            self._information_repository = InformationRepository(self.queue)
        return self._information_repository

    @property
    def referral_repository(self) -> ReferralRepository:
        if self._referral_repository is None:
            self._referral_repository = ReferralRepository(self.queue)
        return self._referral_repository

    @property
    def school_admin_repository(self) -> SchoolAdminRepository:
        if self._school_admin_repository is None:
            self._school_admin_repository = SchoolAdminRepository(self.queue)
        return self._school_admin_repository

    @property
    def school_post_repository(self) -> SchoolPostRepository:
        if self._school_post_repository is None:
            self._school_post_repository = SchoolPostRepository(self.queue)
        return self._school_post_repository

    @property
    def tgbot_state_repository(self) -> TgbotStateRepository:
        if self._tgbot_state_repository is None:
            self._tgbot_state_repository = TgbotStateRepository(self.queue)
        return self._tgbot_state_repository

    @property
    def school_post_vision_repository(self) -> SchoolPostVisionRepository:
        if self._school_post_vision_repository is None:
            self._school_post_vision_repository = SchoolPostVisionRepository(self.queue)
        return self._school_post_vision_repository

    @property
    def school_post_click_repository(self) -> SchoolPostClickRepository:
        if self._school_post_click_repository is None:
            self._school_post_click_repository = SchoolPostClickRepository(self.queue)
        return self._school_post_click_repository

    @property
    def school_post_viewing_repository(self) -> SchoolPostViewingRepository:
        if self._school_post_viewing_repository is None:
            self._school_post_viewing_repository = SchoolPostViewingRepository(self.queue)
        return self._school_post_viewing_repository

    @property
    def school_post_like_repository(self) -> SchoolPostLikeRepository:
        if self._school_post_like_repository is None:
            self._school_post_like_repository = SchoolPostLikeRepository(self.queue)
        return self._school_post_like_repository

    @property
    def ad_repository(self) -> AdRepository:
        if self._ad_repository is None:
            self._ad_repository = AdRepository(self.queue)
        return self._ad_repository

    @property
    def ad_viewing_repository(self) -> AdViewingRepository:
        if self._ad_viewing_repository is None:
            self._ad_viewing_repository = AdViewingRepository(self.queue)
        return self._ad_viewing_repository
