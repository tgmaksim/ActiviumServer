from datetime import timedelta
from typing import Optional, Union

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert

from ...models.cache_model import Cache
from ...models.session_model import Session
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['CacheRepository']


class CacheRepository(SqlAlchemyRepository[Cache]):
    """Репозиторий для взаимодействия с записями кэша"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Cache)

    async def put_caches(
            self,
            session_id: str,
            child_id: int,
            caches: list[tuple[str, Union[list, dict]]]
    ) -> list[Cache]:
        """
        Вставить или изменить несколько записей кэша

        :param session_id: идентификатор сессии, к которой привязаны записи кэша
        :param child_id: идентификатор ребенка, к которому привязаны записи кэша
        :param caches: список пар (ключ, значение JSON)
        :return: записи кэша
        """

        statement = insert(Cache).values([{
            'session_id': session_id,
            'child_id': child_id,
            'key': cache[0],
            'value': cache[1]
        } for cache in caches])

        # В случае существования записи ее значение редактируется
        statement = statement.on_conflict_do_update(
            index_elements=('session_id', 'child_id', 'key'),
            set_={
                'value': statement.excluded.value
            }
        )

        statement = statement.returning(Cache)

        res = await self.queue.execute(statement)

        return list(res.scalars().all())

    async def put_cache(
            self,
            session_id: str,
            child_id: int,
            cache_key: str,
            cache_value: Union[list, dict]
    ) -> Cache:
        """
        Вставить или изменить одну запись кэша

        :param session_id: идентификатор сессии, к которой привязана запись кэша
        :param child_id: идентификатор ребенка, к которому привязана запись кэша
        :param cache_key: ключ к записи кэша
        :param cache_value: значение в виде JSON
        :return: запись кэша
        """

        return (await self.put_caches(session_id, child_id, [(cache_key, cache_value)]))[0]

    async def get_caches(self, session_id: str, child_id: int, keys: list[str]) -> list[Cache]:
        """
        Получение нескольких записей кэша

        :param session_id: идентификатор сессии, к которой привязаны записи кэша
        :param child_id: идентификатор ребенка, к которой привязаны записи кэша
        :param keys: ключи кэша
        :return: список существующих записей кэша
        """

        return await self.get_multi(
            Cache.session_id == session_id, Cache.child_id == child_id, Cache.key.in_(keys))

    async def get_cache(self, session_id: str, child_id: int, key: str) -> Optional[Cache]:
        """
        Получение одной записи кэша

        :param session_id: идентификатор сессии, к которой привязана запись кэша
        :param child_id: идентификатор ребенка, к которой привязана запись кэша
        :param key: ключ кэша
        :return: запись кэша, если такая существует
        """

        return await self.get_single(
            Cache.session_id == session_id, Cache.child_id == child_id, Cache.key == key)

    async def delete_unregistered_cache(self):
        """Удаление записей кэша, которые привязаны с неработающим сессиям"""

        return await self.delete(Cache.session_id.in_(select(Session.session_id).where(Session.life == False)))

    async def delete_old_cache(self, lifetime: timedelta):
        """Удаление старого кэша"""

        return await self.delete((func.now() - Cache.created_at) > lifetime)
