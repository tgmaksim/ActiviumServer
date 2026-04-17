from enum import Enum
from typing import Optional, Union
from datetime import datetime

from sqlalchemy import select, func

from .db_queue import AsyncDBQueue
from .sqlalchemy_repository import SqlAlchemyRepository

from ..models.statistic_model import Statistic


__all__ = ['StatisticRepository', 'StatName']


class StatName(Enum):
    ea_notifications = "Отправлено уведомление с напоминанием о внеурочном занятии"
    marks_notifications = "Отправлено уведомление о новой оценке"
    getFinalMarks = "Запрос годовых оценок"
    getLessonRatingStats = "Запрос статистики по уроку с рейтингом в классе"
    getMarks = "Запрос своих оценок за текущий период"
    getMarksRatingStats = "Запрос статистики по оценке с рейтингом в классе"
    getMarksSubjectRating = "Запрос рейтинга по предмету"
    getSchedule = "Запрос расписания"
    createNote = "Создание заметки к уроку"
    deleteNote = "Удаление заметки к уроку"
    highlightPerson = "Выделение одноклассника в рейтингах для отображения вверху"
    unhighlightPerson = "Отмена выделения одноклассника"
    sendPraise = "Отправка похвалы от родителя ребенку за получение оценки"
    registration = "Регистрация нового пользователя"
    authorization = "Повторная авторизация пользователя"
    checkSession = "Проверка авторизации сессии"
    login = "Создание сессии для последующей авторизации"
    createReview ="Создание отзыва"
    deleteReview = "Удаление отзыва"
    likeReview = "Реакции (лайк) на чужой отзыв"
    deleteReviewLike = "Удаление реакции на отзыв"
    getChildren = "Запрос своих профилей (у родителей - детей, у ребенка - только самого себя)"
    setActiveChild = "Выбор активного профиля"
    turnOnEANotifications = "Включение уведомлений с напоминанием о внеурочных занятиях"
    turnOffEANotifications = "Выключению уведомлений с напоминанием о внеурочных занятиях"
    turnOnMarksNotifications = "Включение уведомлений о новых оценках"
    turnOffMarksNotifications = "Выключение уведомлений о новых оценках"
    updateFirebase = "Обновление токена firebase (каждый раз при входе)"
    site = "Посещение сайта"
    checkInfoNotifications = "Проверка наличия информационных уведомлений (каждый раз при входе)"
    checkVersion = "Проверка версии приложения (каждый рах при входе)"


class StatisticRepository(SqlAlchemyRepository[Statistic]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Statistic)

    async def add_statistic(self, parent_id: Optional[int], key: Union[StatName, str]):
        await self.create({
            "parent_id": parent_id,
            "key": key.name if isinstance(key, Enum) else key
        })

    async def get_count_unique_users(self, since: datetime) -> int:
        statement = select(func.count(func.distinct(Statistic.parent_id))).where(Statistic.created_at > since)

        res = await self.queue.execute(statement)
        return res.scalar_one()

    async def get_group_statistics(self, since: datetime) -> list[tuple[str, int]]:
        """[(key, count), ...]"""

        statement = select(Statistic.key, func.count().label('count')).where(Statistic.created_at > since).group_by(Statistic.key)

        res = await self.queue.execute(statement)
        return res.all()
