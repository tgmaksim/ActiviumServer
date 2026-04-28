from .db_queue import AsyncDBQueue
from ..models.statistic_message_model import StatisticMessage

from sqlalchemy import func
from .sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['StatisticMessageRepository']


class StatisticMessageRepository(SqlAlchemyRepository[StatisticMessage]):
    """Репозиторий для работы с составленными отчетами"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, StatisticMessage)

    async def get_last_messages(self, count: int = 5) -> list[StatisticMessage]:
        """Получение последних n отчетов"""

        return await self.get_multi(orders_=StatisticMessage.time.desc(), limit=count)

    async def write_message(self, message: str) -> StatisticMessage:
        """Добавить новый отчет"""

        return await self.create({
            'time': func.now(),
            'message': message
        })