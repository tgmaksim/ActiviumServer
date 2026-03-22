from typing import Optional

from .db_queue import AsyncDBQueue
from .sqlalchemy_repository import SqlAlchemyRepository

from ..models.log_model import Log


__all__ = ['LogRepository']


class LogRepository(SqlAlchemyRepository[Log]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Log)

    async def add_log(
            self,
            *,
            ip: Optional[str] = None,
            path: str,
            session_id: Optional[str] = None,
            status: bool = True,
            method: Optional[str] = None,
            value: str,
    ) -> Log:
        return await self.create({
            'ip': ip,
            'path': path,
            'session_id': session_id,
            'status': status,
            'method': method,
            'value': value
        })
