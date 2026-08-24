import asyncio

from typing import Any

from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession


__all__ = ['AsyncDBQueue']


class AsyncDBQueue:
    """
    Класс соединения для одновременных асинхронных запросов без ошибки конкурентности.
    Worker ждет запросов и ставит их в очередь на обработку. Обрабатывает последовательно.
    При этом можно запускать в разных задачах одновременно
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.queue = asyncio.Queue()
        self._worker_task = None

    async def start(self):
        """Запуск worker'а с ожиданием запросов"""

        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Остановка worker'а и ожидание завершения работы"""

        await self.queue.put((None, None))
        await self._worker_task

    async def _worker(self):
        while True:
            statement, future = await self.queue.get()  # Получение следующей задачи с ожиданием
            if statement is None:  # При передаче (None, None) worker останавливается
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
                self.queue.task_done()  # Задача выполнена и результат возвращен обратно

    async def rollback(self) -> None:
        """Помещение в очередь действия отката назад"""

        future = asyncio.get_running_loop().create_future()
        await self.queue.put(('rollback', future))
        return await future

    async def commit(self) -> None:
        """Помещение в очередь commit'а изменений"""

        future = asyncio.get_running_loop().create_future()
        await self.queue.put(('commit', future))
        return await future

    async def execute(self, statement: Executable) -> Result[Any]:
        """Помещение в очередь выполнения запроса"""

        future = asyncio.get_running_loop().create_future()
        await self.queue.put((statement, future))
        return await future
