from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .hour_repository import HourRepository
from .child_repository import ChildRepository
from .cache_repository import CacheRepository
from .review_repository import ReviewRepository
from .parent_repository import ParentRepository
from .rating_repository import RatingRepository
from .session_repository import SessionRepository
from .version_repository import VersionRepository
from .lesson_note_repository import LessonNoteRepository
from ...repositories.log_repository import LogRepository
from .review_likes_repository import ReviewLikeRepository
from .ea_notification_repository import EANotificationRepository
from ...repositories.statistic_repository import StatisticRepository
from .marks_notification_repository import MarksNotificationRepository
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
