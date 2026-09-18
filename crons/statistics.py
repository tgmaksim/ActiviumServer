from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory

from src.utils.exception import format_exception


__all__ = ['main']


async def main():
    """Обработка собранной статистики и отправка отчета"""

    service = LogService(get_log_uow_factory())
    try:
        await service.send_stats_notification()
    except Exception as e:
        error = format_exception(e)
        print(error)
        await service.log(
            path='statistics',
            status=False,
            value=error
        )
