import time
import asyncio
import traceback

from typing import Callable, Optional
from datetime import datetime, timedelta, UTC

from httpx import AsyncClient
from asyncio import AbstractEventLoop, Task

from firebase.messaging import send_notifications, Notification, AppNotificationChannel, FCMResult

from src.services.log_service import LogService
from src.models.lesson_note_model import LessonNote
from src.dependencies.uow import get_log_uow_factory
from src.repositories.statistic_repository import StatName
from src.support.repositories.app_uow import AppUnitOfWork


CYCLE_SECONDS = 4 * 60
WINDOW_START_MINUTES = 0
WINDOW_END_MINUTES = 5

__all__ = ['RemindLessonNotesWorker', 'add_work']


class RemindLessonNotesWorker:
    """
    Класс для работы уведомлений с напоминаниями о заметках к урокам

    За каждый проход в несколько этапов берутся все напоминания, которые запланированы на ближайшие 5 минут.
    Для каждой заметки отправляется уведомление всем сессиям ребенка (без родителей)

    Так происходит пока ближайших напоминаний о заметках к урокам не останется.
    После процесс приостанавливается на 4 минуты
    """

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        self._running = False
        self.uow_factory = uow_factory
        self.httpx_client = httpx_client

    async def run(self):
        self._running = True

        service = LogService(get_log_uow_factory())
        await service.log(
            ip='notes_notifications',
            path='notes_notifications',
            value="Worker запущен"
        )
        print("notes_notifications запущен")

        try:
            while self._running:
                start = time.monotonic()

                try:
                    now = datetime.now(UTC)
                    start_period = now + timedelta(minutes=WINDOW_START_MINUTES)
                    end_period = now + timedelta(minutes=WINDOW_END_MINUTES)

                    async with self.uow_factory() as uow:
                        # Все заметки, у которых есть напоминания в ближайшие 5 минут
                        rows = await uow.lesson_note_repository.get_next_notes_to_remind(
                            (start_period, end_period))

                        # Уведомления, которые нужно отправить
                        pushes = await self._process_batch(uow, rows)

                        # Результат отправки каждого уведомления
                        response = await self._dispatch_pushes(pushes)

                        for firebase_token, result in (response.results if response else []):
                            status = result.exception is None
                            await uow.log_repository.add_log(
                                ip='notes_notifications',
                                path=firebase_token,
                                status=status,
                                value=f"{result.exception}: {result.exception.http_response} {result.exception.cause} "
                                      f"{result.exception.http_response.__dict__}" if not status else str(result)
                            )
                except Exception as e:
                    service = LogService(get_log_uow_factory())
                    await service.log(
                        ip='notes_notifications',
                        path='notes_notifications',
                        status=False,
                        value='\n'.join(traceback.format_exception(e))
                    )

                elapsed = time.monotonic() - start

                await asyncio.sleep(CYCLE_SECONDS - elapsed)
        except Exception as e:
            service = LogService(get_log_uow_factory())
            await service.log(
                ip='notes_notifications',
                path='notes_notifications',
                status=False,
                value='\n'.join(traceback.format_exception(e))
            )
        finally:
            print("notes_notifications остановлен")
            service = LogService(get_log_uow_factory())
            await service.log(
                ip='notes_notifications',
                path='notes_notifications',
                value="Worker остановлен"
            )

    @classmethod
    async def _process_batch(cls, uow: AppUnitOfWork, rows: list[LessonNote]) -> list[tuple[str, dict]]:
        """
        Создание уведомлений с напоминанием о заметке к урокам

        :return: список параметров уведомлений (firebase-токен, параметры заметки)
        """

        if not rows:
            return []

        # Дети, задействованные в текущем проходе
        children = {row.child_id: row.child for row in rows}

        # Сессии детей (родители не получают уведомления) с firebase-токенами
        sessions: dict[int, set[str]] = {}
        for child_id, child in children.items():
            if child_id not in sessions:
                sessions[child_id] = set()
            # Сессии ребенка как пользователя (без родителей)
            child_sessions = await uow.session_repository.get_sessions(child_id)
            sessions[child_id].update(child_session.firebase_token for child_session in child_sessions)

        pushes: list[tuple[str, dict]] = []

        for row in rows:
            payload = {
                "text": row.text
            }

            pushes.extend([(firebase_token, payload) for firebase_token in sessions[row.child_id]])

        for child_id, firebase_tokens in sessions.items():
            if len(firebase_tokens) != 0:
                await uow.statistic_repository.add_statistic(child_id, StatName.notes_notifications)

        for row in rows:
            # Удаление напоминания для заметки
            await uow.lesson_note_repository.delete_note_remind(row.child_id, row.lesson_id)

        return pushes

    @classmethod
    async def _dispatch_pushes(cls, pushes: list[tuple[str, dict]]) -> Optional[FCMResult]:
        """Отправка уведомлений"""

        if not pushes:
            return None

        return await send_notifications([Notification(
            firebase_token=firebase_token,
            title="Напоминание о заметке",
            message=activity['text'],
            channel=AppNotificationChannel.notes,
            data={"from_notification": "remind_note"}
        ) for firebase_token, activity in pushes])

    def stop(self):
        self._running = False


def add_work(loop: AbstractEventLoop, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient) -> Task:
    worker = RemindLessonNotesWorker(uow_factory, httpx_client)
    return loop.create_task(worker.run())
