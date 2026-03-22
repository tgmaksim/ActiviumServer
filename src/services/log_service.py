from typing import Optional

from .base_service import BaseService
from ..repositories.log_uow import LogUnitOfWork


__all__ = ['LogService']


class LogService(BaseService[LogUnitOfWork]):
    async def log(
            self,
            *,
            ip: Optional[str] = None,
            path: str,
            session_id: Optional[str] = None,
            status: bool = True,
            method: Optional[str] = None,
            value: str,
    ):
        async with self.uow_factory() as uow:
            await uow.log_repository.add_log(ip=ip, path=path, session_id=session_id, status=status, method=method, value=value)

    async def send_stats_notification(self):
        async with self.uow_factory() as uow:
            count_all, max_created_at, min_created_at, count_errors = await uow.notification_repository.get_count()

            from_date = max_created_at.strftime('%e %b. %H:%M:%S')
            ru_logs = 'лога' if 2 <= count_all % 10 <= 4 else ('лог' if count_all % 10 == 1 else 'логов')

            text = (f"<b>Статистика Гимназии c {from_date}</b>\n\n"
                    f"<b>Логи</b>\nСобрано {count_all} {ru_logs}\n")

            if count_errors:
                text += f"⚠️ Обнаружены ошибки ({count_errors} шт.)\n"
            else:
                text += "Ошибок не обнаружено\n"

            await uow.notification_repository.delete_notifications(max_created_at)
            await uow.log_repository.add_log(path='stats', value='stats')  # Для точной статистики в следующий раз

            since = min_created_at

            text += "\n<b>Мониторинг запросов</b>\n"
            monitorings = await uow.monitoring_repository.get_stats(since)
            for monitoring in monitorings:
                text += (f"<i>{monitoring[0]}</i>: "
                         f"от {round(monitoring[1].total_seconds() * 1000, 1)} мс "
                         f"до {round(monitoring[2].total_seconds() * 1000, 1)} мс, "
                         f"{round(monitoring[3].total_seconds() * 1000, 1)} мс\n")

            text += "\n<b>Статистика пользования</b>\n"
            count_unique_users = await uow.statistics_repository.get_count_unique_users(since)
            text += f"Уникальных пользователей: {count_unique_users}\n"
            group_statistics = await uow.statistics_repository.get_group_statistics(since)
            for statistic in group_statistics:
                text += f"<i>{statistic[0]}</i>: {statistic[1]}\n"

            text += "\n<i>Таким был день в Гимназии...</i>"

            await uow.notification_repository.notify(text)

