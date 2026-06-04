from typing import Optional

from ...models.rating_model import Rating
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['RatingRepository']


class RatingRepository(SqlAlchemyRepository[Rating]):
    """Репозиторий для работы с прошлым местом в рейтинге"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Rating)

    async def put_rating(
            self,
            child_id: int,
            period_id: int,
            subject_id: int,
            number: int,
            avg: str,
            mood: str
    ) -> Rating:
        """
        Запись (или обновление) места в рейтинге ребенка (профиля)

        :param child_id: идентификатор ребенка (профиля)
        :param period_id: идентификатор отчетного периода, взятый из Дневника.ру
        :param subject_id: идентификатор учебного предмета
        :param number: место в рейтинге (индекс — начало с 0)
        :param avg: средний балл по предмету
        :param mood: "настроение" среднего балла
        :return: запись места в рейтинге
        """

        return await self.create({
            'child_id': child_id,
            'period_id': period_id,
            'subject_id': subject_id,
            'number': number,
            'avg': avg,
            'mood': mood
        }, security=['child_id', 'period_id', 'subject_id'])

    async def get_rating(self, child_id: int, period_id: int, subject_id: int) -> Optional[Rating]:
        """
        Получение прошлого места в рейтинге

        :param child_id: идентификатор ребенка (профиля)
        :param period_id: идентификатор отчетного периода, взятый из Дневника.ру
        :param subject_id: идентификатор учебного предмета
        :return: прошлое места в рейтинге, если было записано
        """

        return await self.get_single(
            Rating.child_id == child_id, Rating.period_id == period_id, Rating.subject_id == subject_id)

    async def delete_rating(self, child_id: int, period_id: int, subject_id: int):
        """
        Удаление записи места в рейтинге

        :param child_id: идентификатор ребенка (профиля)
        :param period_id: идентификатор отчетного периода, взятый из Дневника.ру
        :param subject_id: идентификатор учебного предмета
        """

        return await self.delete(
            Rating.child_id == child_id, Rating.period_id == period_id, Rating.subject_id == subject_id)
