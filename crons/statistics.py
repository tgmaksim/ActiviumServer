import traceback

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory


async def main():
    service = LogService(get_log_uow_factory())
    try:
        await service.send_stats_notification()
    except Exception as e:
        print(''.join(traceback.format_exception(e)))
        await service.log(
            path='statistics',
            status=False,
            value=f"{e.__class__.__name__}: {e}"
        )
