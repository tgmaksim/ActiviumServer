from typing import Optional

from ...models.version_model import Version
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['VersionRepository']


class VersionRepository(SqlAlchemyRepository[Version]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Version)

    async def get_all_versions(self) -> list[Version]:
        return await self.get_multi(orders_=Version.number.desc())

    async def get_latest_version(self) -> Optional[Version]:
        return await self.get_first(orders_=Version.number.desc())

    async def get_most_important_version(self, version_number: int) -> Optional[Version]:
        return await self.get_first(Version.number > version_number, orders_=Version.status_id.desc())
