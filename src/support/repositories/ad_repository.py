from typing import Optional
from datetime import timedelta

from sqlalchemy.sql import select, or_
from sqlalchemy.sql.functions import func

from ...models.ad_model import Ad
from ...repositories.db_queue import AsyncDBQueue
from ...models.ad_viewing_model import AdViewingModel

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['AdRepository']


class AdRepository(SqlAlchemyRepository[Ad]):
    """Репозиторий для взаимодействия с рекламными объявлениями"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Ad)

    async def get_accessible_ads(self, parent_id: int, school_id: int, group_id: int, min_last_viewing_delta: timedelta) -> list[tuple[int, Optional[timedelta]]]:
        """
        Получение идентификаторов и времени от последнего просмотра доступных для пользователя рекламных объявлений

        :param parent_id: идентификатор пользователя
        :param school_id: идентификатор образовательной организации
        :param group_id: идентификатор учебной группы (класса)
        :param min_last_viewing_delta: минимальный период с момента прошлого показа для доступа
        :return: список идентификаторов рекламных объявлений
        """

        statement = (
            select(Ad.ad_id, (last_viewing_delta := (func.now() - AdViewingModel.last_viewing).label('last_viewing_delta')))
            .outerjoin(
                AdViewingModel,
                (AdViewingModel.ad_id == Ad.ad_id) & (AdViewingModel.parent_id == parent_id)
            )
            .where(
                or_(Ad.school_id == school_id, Ad.school_id.is_(None)),
                or_(Ad.group_id == group_id, Ad.group_id.is_(None)),
                Ad.balance > 0,
                or_(AdViewingModel.last_viewing.is_(None), last_viewing_delta > min_last_viewing_delta)
            )
        )

        res = await self.queue.execute(statement)
        return res.all()

    async def get_ad(self, ad_id: int) -> Optional[Ad]:
        """
        Получение рекламного объявления по его идентификатору

        :param ad_id: идентификатор рекламного объявления
        :return: рекламное объявление, если есть
        """

        return await self.get_single(Ad.ad_id == ad_id)

    async def see_ad(self, ad_id: int) -> Optional[Ad]:
        """
        Уменьшить баланс рекламного объявления

        :param ad_id: идентификатор рекламного объявления
        :return: обновленное рекламное объявление, если существует
        """

        return await self.update({'balance': Ad.balance - 1}, Ad.ad_id == ad_id)

    async def click_ad(self, ad_id: int) -> Optional[Ad]:
        """
        Увеличить счетчик кликов у рекламного объявления

        :param ad_id: идентификатор рекламного объявления
        :return: обновленное рекламное объявление, если существует
        """

        return await self.update({'clicks': Ad.clicks + 1}, Ad.ad_id == ad_id)
