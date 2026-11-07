from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.web_version_model import WebVersion

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['WebVersionRepository']


class WebVersionRepository(SqlAlchemyRepository[WebVersion]):
    """Репозиторий для работы с версиями web-приложения"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, WebVersion)

    async def get_all_versions(self, only_generic: bool = True) -> list[WebVersion]:
        """
        Получить все версии web-приложения

        :param only_generic: только общие версии (без мини-версий)
        :return: список версий приложения
        """

        if only_generic:
            return await self.get_multi(WebVersion.parent_version == None, orders_=WebVersion.number.desc())
        return await self.get_multi(orders_=WebVersion.number.desc())

    async def get_latest_version(self) -> Optional[WebVersion]:
        """
        Получить последнюю версию web-приложения

        :return: последняя версия, если существует
        """

        return await self.get_first(orders_=WebVersion.number.desc())

    async def get_latest_generic_version(self) -> Optional[WebVersion]:
        """
        Получить последнюю общую версию web-приложения

        :return: последняя общая версия, если существует
        """

        return await self.get_first(WebVersion.parent_version == None, orders_=WebVersion.number.desc())

    async def get_latest_mini_versions(self, latest_generic_version: int) -> list[WebVersion]:
        """
        Получить все последние мини-версии для последней общей версии

        :param latest_generic_version: номер последней общей версии
        """

        return await self.get_multi(WebVersion.parent_version != None, WebVersion.number > latest_generic_version, orders_=WebVersion.number.desc())

    async def get_most_important_version(self, version_number: int) -> Optional[WebVersion]:
        """
        Получить самую важную (по status_id) версию после данной

        :param version_number: номер текущей версии
        :return: самая важная версия, если существует
        """

        return await self.get_first(WebVersion.number > version_number, orders_=WebVersion.status_id.desc())

    async def get_younger_versions(self, version_number: int) -> list[WebVersion]:
        """
        Получить все версии, которые новее данной

        :param version_number: номер текущей версии
        :return: список свежих версий
        """

        return await self.get_multi(WebVersion.number > version_number, orders_=WebVersion.number.asc())
