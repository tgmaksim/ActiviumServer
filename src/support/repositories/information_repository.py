from datetime import datetime

from sqlalchemy import func

from ...repositories.db_queue import AsyncDBQueue
from ...models.information_model import Information

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['InformationRepository']


class InformationRepository(SqlAlchemyRepository[Information]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Information)

    async def create_information(self, parent_id: int, type_: str, time: datetime, title: str, text: str) -> Information:
        return await self.create({
            'parent_id': parent_id,
            'time': time,
            'type': type_,
            'title': title,
            'text': text
        })

    async def get_informations(self, parent_id: int) -> list[Information]:
        return await self.get_multi(Information.parent_id == parent_id, Information.time <= func.now())

    async def delete_information(self, parent_id: int, time: datetime, type_: str):
        return await self.delete(Information.parent == parent_id, Information.type == type_, Information.time == time)

    async def delete_informations(self, parent_id: int):
        return await self.delete(Information.parent_id == parent_id, Information.time <= func.now())
