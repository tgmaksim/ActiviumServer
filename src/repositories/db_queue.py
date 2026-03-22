import asyncio

from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession


__all__ = ['AsyncDBQueue']


class AsyncDBQueue:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.queue = asyncio.Queue()
        self._worker_task = None

    async def start(self):
        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        await self.queue.put((None, None))
        await self._worker_task

    async def _worker(self):
        while True:
            statement, future = await self.queue.get()
            if statement is None:
                break

            try:
                if statement == 'rollback':
                    result = await self.session.rollback()
                elif statement == 'commit':
                    result = await self.session.commit()
                else:
                    result = await self.session.execute(statement)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()

    async def rollback(self):
        future = asyncio.get_running_loop().create_future()
        await self.queue.put(('rollback', future))
        return await future

    async def commit(self):
        future = asyncio.get_running_loop().create_future()
        await self.queue.put(('commit', future))
        return await future

    async def execute(self, statement: Executable):
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((statement, future))
        return await future
