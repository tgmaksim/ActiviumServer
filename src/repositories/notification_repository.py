from datetime import datetime

from sqlalchemy import select, func

from tgbot.notifier import send_admin_message

from .db_queue import AsyncDBQueue
from .sqlalchemy_repository import SqlAlchemyRepository

from ..models.notification_model import Notification


__all__ = ['NotificationRepository']


class NotificationRepository(SqlAlchemyRepository[Notification]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Notification)

    async def get_count(self) -> tuple[int, datetime, datetime, int]:
        """(count_all, max_created_at, min_created_at, count_errors)"""

        statement = select(
            func.count(Notification.log_id).label('count_all'),
            func.max(Notification.created_at).label('max_created_at'),
            func.min(Notification.created_at).label('min_created_at'),
            func.count(Notification.log_id).filter(Notification.status.is_(False)).label('count_errors')
        )

        res = await self.queue.execute(statement)
        row = res.mappings().one()
        return row['count_all'], row['max_created_at'], row['min_created_at'], row['count_errors']

    async def delete_notifications(self, max_created_at: datetime) -> int:
        return await self.delete(Notification.created_at <= max_created_at)

    @staticmethod
    async def notify(message: str):
        await send_admin_message(message)
