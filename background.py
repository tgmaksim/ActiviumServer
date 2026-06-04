import asyncio
import argparse


__all__ = ['add_backgrounds']


def add_backgrounds(
        loop: asyncio.AbstractEventLoop,
        *,
        tgbot: bool = False,
        marks_notifications: bool = False,
        ea_notifications: bool = False,
        notes_notifications: bool = False
) -> list[asyncio.Task]:
    """
    Добавить фоновые задачи в event loop

    :param loop: async event loop
    :param tgbot: запустить Telegram-бота
    :param marks_notifications: запустить проверку новых оценок
    :param ea_notifications: запустить напоминания о внеурочных занятиях
    :param notes_notifications: запустить напоминания о заметках к урокам
    :return: список созданных задач
    """

    tasks = []

    from src.dependencies.httpx import get_httpx_client
    from src.dependencies.uow import get_app_uow_factory

    if tgbot:
        from tgbot.main import add_polling_task
        add_polling_task(loop)

    if marks_notifications:
        from backgrounds.marks_notifications import add_work as add_marks_work
        add_marks_work(loop, get_app_uow_factory(), get_httpx_client())

    if ea_notifications:
        from backgrounds.ea_notifications import add_work as add_ea_work
        add_ea_work(loop, get_app_uow_factory(), get_httpx_client())

    if notes_notifications:
        from backgrounds.notes_notifications import add_work as add_notes_work
        add_notes_work(loop, get_app_uow_factory(), get_httpx_client())

    return tasks


def start_backgrounds(**params):
    """
    Запуск фоновых задач в текущем процессе

    :param params: какие задачи запускать
    """

    loop = asyncio.new_event_loop()
    tasks = add_backgrounds(loop, **params)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for t in tasks:
            t.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск фоновых процессов. Допускается одновременный запуск нескольких")
    parser.add_argument('--tgbot', action='store_true', help="Запустить Telegram-бота")
    parser.add_argument('--marks-notifications', action='store_true',
                        help="Запустить worker уведомлений о новых оценках")
    parser.add_argument('--ea-notifications', action='store_true',
                        help="Запустить worker уведомлений с напоминанием о внеурочном занятии")
    parser.add_argument('--notes-notifications', action='store_true',
                        help="Запустить worker уведомлений с напоминаниями о заметках к урокам")
    args = parser.parse_args()

    start_backgrounds(
        tgbot=args.tgbot,
        marks_notifications=args.marks_notifications,
        ea_notifications=args.ea_notifications,
        notes_notifications=args.notes_notifications
    )
