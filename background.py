import asyncio

from ea_notifications import add_work as add_ea_work
from marks_notifications import add_work as add_marks_work

from src.dependencies.httpx import get_httpx_client
from src.dependencies.uow import get_app_uow_factory

from tgbot.main import add_polling_task


__all__ = ['add_backgrounds']


def add_backgrounds(loop: asyncio.AbstractEventLoop) -> list[asyncio.Task]:
    tasks = [
        add_polling_task(loop),
        add_marks_work(loop, get_app_uow_factory(), get_httpx_client()),
        add_ea_work(loop, get_app_uow_factory(), get_httpx_client())
    ]

    return tasks


def start_backgrounds():
    loop = asyncio.get_event_loop()
    tasks = add_backgrounds(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for t in tasks:
            t.cancel()


if __name__ == "__main__":
    start_backgrounds()
