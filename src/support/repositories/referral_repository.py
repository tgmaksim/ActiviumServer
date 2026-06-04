from typing import Optional

from sqlalchemy import select, func

from ...models.refferal_model import Referral
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ReferralRepository']


class ReferralRepository(SqlAlchemyRepository[Referral]):
    """Репозиторий для взаимодействия с приглашениями новых пользователей"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Referral)

    async def link_referral(self, parent_id: int, referral_id: int, name: str) -> Referral:
        """
        Связать нового пользователя как приглашенного другим. Если он уже связан, то данные не обновятся

        :param parent_id: идентификатор пользователя, который пригласил
        :param referral_id: идентификатор нового пользователя
        :param name: имя пользователя, который пригласил
        :return: параметры приглашенного пользователя
        """

        return await self.create({
            'parent_id': parent_id,
            'referral_id': referral_id,
            'name': name
        }, security=['referral_id'], security_nothing=True)

    async def get_count_my_referrals(self, parent_id: int) -> int:
        """
        Подсчет количества приглашенных пользователей

        :param parent_id: идентификатор пользователя
        :return: число приглашенных пользователей
        """

        statement = select(func.count()).where(Referral.parent_id == parent_id)

        res = await self.queue.execute(statement)
        return res.scalar_one()

    async def get_me_referral(self, parent_id: int) -> Optional[Referral]:
        """
        Получение параметров пользователя, который пригласил

        :param parent_id: идентификатор приглашенного пользователя
        :return: параметры приглашения, если существуют
        """

        return await self.get_single(Referral.referral_id == parent_id)
