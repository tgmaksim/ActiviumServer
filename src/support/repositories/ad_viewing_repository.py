from typing import Optional

from sqlalchemy.sql.functions import func

from ...repositories.db_queue import AsyncDBQueue
from ...models.ad_viewing_model import AdViewingModel

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository

__all__ = ['AdViewingRepository']


class AdViewingRepository(SqlAlchemyRepository[AdViewingModel]):
    """Репозиторий для взаимодействия с просмотрами рекламных объявлений"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, AdViewingModel)

    async def see_ad(self, ad_id: int, parent_id: int) -> Optional[AdViewingModel]:
        """
        Записать показ рекламного объявления

        :param ad_id: идентификатор рекламного объявления
        :param parent_id: идентификатор пользователя
        :return: запись показа рекламного объявления
        """

        return await self.create({
            'ad_id': ad_id,
            'parent_id': parent_id,
            'last_viewing': func.now()
        }, security=['ad_id', 'parent_id'])
