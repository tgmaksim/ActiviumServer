from asyncpg.pgproto.pgproto import timedelta

from src.dependencies.uow import get_app_uow_factory


SESSION_LIFETIME = timedelta(days=64)
LESSON_NOTE_LIFETIME = timedelta(days=32)


async def main():
    uow_factory = get_app_uow_factory()

    async with uow_factory() as uow:
        await uow.session_repository.kill_old_sessions(SESSION_LIFETIME)
        await uow.cache_repository.delete_unregistered_cache()
        await uow.ea_processing_notification_repository.delete_overdue_ea()
        await uow.lesson_note_repository.delete_old_note(LESSON_NOTE_LIFETIME)

        await uow.log_repository.add_log(ip='127.0.0.1', path='clear', method='DELETE', value="Success")
