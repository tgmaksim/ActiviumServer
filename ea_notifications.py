import asyncio
import traceback

from math import ceil
from typing import Callable
from datetime import datetime, timedelta, UTC

from httpx import AsyncClient
from asyncio import AbstractEventLoop

from firebase.messaging import send_notifications, Notification, AppNotificationChannel

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory
from src.support.repositories.app_uow import AppUnitOfWork
from src.models.ea_processing_notification_model import EAProcessingNotification


CYCLE_SECONDS = 8 * 60
WINDOW_START_MINUTES = 5
WINDOW_END_MINUTES = 15

__all__ = ['EAProcessingNotification', 'add_work']


class ExtracurricularActivityWorker:
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        self._running = True
        self.uow_factory = uow_factory
        self.httpx_client = httpx_client

    async def run(self):
        service = LogService(get_log_uow_factory())
        await service.log(
            path='ea_notifications',
            value="Worker запущен"
        )
        print("ea_notifications запущен")

        try:
            while self._running:
                try:
                    while self._running:
                        now = datetime.now(UTC)
                        start_period = now + timedelta(minutes=WINDOW_START_MINUTES)
                        end_period = now + timedelta(minutes=WINDOW_END_MINUTES)

                        async with self.uow_factory() as uow:
                            rows = await uow.ea_processing_notification_repository.get_next_extracurricular_activities(
                                (start_period, end_period))

                            if not rows:
                                break

                            pushes, processed_ids = await self._process_batch(uow, rows)
                            await self._dispatch_pushes(pushes)

                            for ea_id in processed_ids:
                                await uow.ea_processing_notification_repository.finish_process(ea_id)
                except Exception as e:
                    service = LogService(get_log_uow_factory())
                    await service.log(
                        path='ea_notifications',
                        status=False,
                        value='\n'.join(traceback.format_exception(e))
                    )
                finally:
                    await asyncio.sleep(CYCLE_SECONDS)
        except Exception as e:
            service = LogService(get_log_uow_factory())
            await service.log(
                path='ea_notifications',
                status=False,
                value='\n'.join(traceback.format_exception(e))
            )
        finally:
            print("ea_notifications остановлен")
            service = LogService(get_log_uow_factory())
            await service.log(
                path='ea_notifications',
                value="Worker остановлен"
            )

    @classmethod
    async def _process_batch(cls, uow: AppUnitOfWork, rows: list[EAProcessingNotification]) -> tuple[list[tuple[str, dict]], list[int]]:
        """Создание уведомлений"""

        if not rows:
            return [], []

        # Все внеурочные занятия с одинаковым start_time
        start_time = rows[0].start_time
        minutes_left = ceil((start_time - datetime.now(UTC)).total_seconds() / 60)

        groups = {(row.extracurricular_activity.school_id, row.extracurricular_activity.group_id) for row in rows}

        notifications = await uow.ea_notification_repository.get_notifications(list(groups))

        children_by_group: dict[tuple[int, int], set[str]] = {}
        for notification in notifications:
            if not notification.session.life:
                await uow.session_repository.kill_session(notification.session_id)
            else:
                key = (notification.child.school_id, notification.child.group_id)
                if children_by_group.get(key) is None:
                    children_by_group[key] = set()
                children_by_group[key].add(notification.session.firebase_token)

        pushes: list[tuple[str, dict]] = []
        processed_ids: list[int] = []

        for row in rows:
            activity = row.extracurricular_activity
            key = (activity.school_id, activity.group_id)

            children = children_by_group.get(key)

            payload = {
                "subject": activity.subject,
                "place": activity.place,
                "minutes_left": minutes_left
            }

            for firebase_token in children:
                pushes.append((firebase_token, payload))

            processed_ids.append(row.ea_id)

        return pushes, processed_ids

    @classmethod
    async def _dispatch_pushes(cls, pushes: list[tuple[str, dict]]):
        """Отправка уведомлений"""

        if not pushes:
            return

        await send_notifications([Notification(
            firebase_token=firebase_token,
            title="Скоро внеурочное занятие",
            message=f"Через {activity['minutes_left']} мин начнётся {activity['subject']} в {activity['place']}",
            channel=AppNotificationChannel.extracurricular_activities
        ) for firebase_token, activity in pushes])

    def stop(self):
        self._running = False


def add_work(loop: AbstractEventLoop, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
    worker = ExtracurricularActivityWorker(uow_factory, httpx_client)
    return loop.create_task(worker.run())
