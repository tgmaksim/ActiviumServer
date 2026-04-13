from typing import Optional

from sqlalchemy import select, func

from ...models.refferal_model import Referral
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ReferralRepository']


class ReferralRepository(SqlAlchemyRepository[Referral]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Referral)

    async def link_referral(self, parent_id: int, referral_id: int, name: str) -> Referral:
        return await self.create({
            'parent_id': parent_id,
            'referral_id': referral_id,
            'name': name
        }, security=['referral_id'], security_nothing=True)

    async def get_count_my_referrals(self, parent_id: int) -> int:
        statement = select(func.count()).where(Referral.parent_id == parent_id)

        res = await self.queue.execute(statement)
        return res.scalar_one()

    async def get_me_referral(self, parent_id: int) -> Optional[Referral]:
        return await self.get_single(Referral.referral_id == parent_id)
