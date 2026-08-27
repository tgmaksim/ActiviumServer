from typing import Optional

from ...models.version_model import Version
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['VersionRepository']


class VersionRepository(SqlAlchemyRepository[Version]):
    """Репозиторий для работы с версиями приложения"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Version)

    async def get_all_versions(self, only_generic: bool = True) -> list[Version]:
        """
        Получить все версии приложения

        :param only_generic: только общие версии (без мини-версий)
        :return: список версий приложения
        """

        if only_generic:
            return await self.get_multi(Version.parent_version == None, orders_=Version.number.desc())
        return await self.get_multi(orders_=Version.number.desc())

    async def get_latest_version(self) -> Optional[Version]:
        """
        Получить последнюю версию приложения

        :return: последняя версия, если существует
        """

        return await self.get_first(orders_=Version.number.desc())

    async def get_latest_generic_version(self) -> Optional[Version]:
        """
        Получить последнюю общую версию приложения

        :return: последняя общая версия, если существует
        """

        return await self.get_first(Version.parent_version == None, orders_=Version.number.desc())

    async def get_latest_mini_versions(self, latest_generic_version: int) -> list[Version]:
        """
        Получить все последние мини-версии для последней общей версии

        :param latest_generic_version: номер последней общей версии
        """

        return await self.get_multi(
            Version.parent_version != None, Version.number > latest_generic_version, orders_=Version.number.desc())

    async def get_most_important_version(self, version_number: int) -> Optional[Version]:
        """
        Получить самую важную (по status_id) версию после данной

        :param version_number: номер текущей версии
        :return: самая важная версия, если существует
        """

        return await self.get_first(Version.number > version_number, orders_=Version.status_id.desc())

    async def get_younger_versions(self, version_number: int) -> list[Version]:
        """
        Получить все версии, которые новее данной

        :param version_number: номер текущей версии
        :return: список свежих версий
        """

        return await self.get_multi(Version.number > version_number, orders_=Version.number.asc())
