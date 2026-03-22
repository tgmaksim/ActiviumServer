from typing import Optional, Union

from sqlalchemy.dialects.postgresql import insert

from ...models.cache_model import Cache
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['CacheRepository']


class CacheRepository(SqlAlchemyRepository[Cache]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Cache)

    async def put_caches(self, session_id: str, caches: list[tuple[str, Union[list, dict]]]) -> list[Cache]:
        statement = insert(Cache).values([{'session_id': session_id, 'key': cache[0], 'value': cache[1]} for cache in caches])
        statement = statement.on_conflict_do_update(
            index_elements=('session_id', 'key'),
            set_={
                'value': statement.excluded.value
            }
        )
        statement = statement.returning(Cache)
        res = await self.queue.execute(statement)
        return list(res.scalars().all())

    async def put_cache(self, session_id: str, cache_key: str, cacheL_value: Union[list, dict]) -> Optional[Cache]:
        return (await self.put_caches(session_id, [(cache_key, cacheL_value)]) or [None])[0]

    async def get_caches(self, session_id: str, keys: list[str]) -> list[Cache]:
        return await self.get_multi(Cache.session_id == session_id, Cache.key.in_(keys))

    async def get_cache(self, session_id: str, key: str) -> Optional[Cache]:
        return await self.get_single(Cache.session_id == session_id, Cache.key == key)
