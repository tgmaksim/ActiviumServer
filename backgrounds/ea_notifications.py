import json
import time
import asyncio
import traceback

from math import ceil
from typing import Callable, Optional
from datetime import datetime, timedelta, UTC

from httpx import AsyncClient
from asyncio import AbstractEventLoop, Task

from firebase.messaging import send_notifications, Notification, AppNotificationChannel, FCMResult

from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory
from src.repositories.statistic_repository import StatName
from src.support.repositories.app_uow import AppUnitOfWork
from src.models.ea_processing_notification_model import EAProcessingNotification


CYCLE_SECONDS = 8 * 60
WINDOW_START_MINUTES = 5
WINDOW_END_MINUTES = 15

__all__ = ['EAProcessingNotification', 'add_work']


class ExtracurricularActivityWorker:
    """
    Класс для работы уведомлений с напоминаниями о внеурочных занятиях

    За каждый проход в несколько этапов берутся все ближайшие внеурочные занятия, которые начнутся не более,
    чем через 15 минут, но до их начала более 5 минут. Для каждого занятия отправляется уведомление всем ученикам класса,
    у кого включены соответствующие уведомления

    Так происходит пока ближайших внеурочных занятий не останется. После процесс приостанавливается на 8 минут
    """

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        self._running = False
        self.uow_factory = uow_factory
        self.httpx_client = httpx_client

    async def run(self):
        self._running = True

        service = LogService(get_log_uow_factory())
        await service.log(
            ip='ea_notifications',
            path='ea_notifications',
            value="Worker запущен"
        )
        print("ea_notifications запущен")

        try:
            while self._running:
                start = time.monotonic()

                try:
                    while self._running:
                        now = datetime.now(UTC)
                        start_period = now + timedelta(minutes=WINDOW_START_MINUTES)
                        end_period = now + timedelta(minutes=WINDOW_END_MINUTES)

                        async with self.uow_factory() as uow:
                            # Ближайшие внеурочные занятия с одинаковым временем начала
                            rows = await uow.ea_processing_notification_repository.get_next_extracurricular_activities(
                                (start_period, end_period))

                            if not rows:
                                break

                            # Уведомления, которые нужно отправить
                            pushes = await self._process_batch(uow, rows)

                            # Результат отправки каждого уведомления
                            response = await self._dispatch_pushes(pushes)

                            for firebase_token, result in (response.results if response else []):
                                status = result.exception is None
                                await uow.log_repository.add_log(
                                    ip='ea_notifications',
                                    path=firebase_token,
                                    status=status,
                                    value=f"{result.exception}: {result.exception.http_response} {result.exception.cause} "
                                          f"{result.exception.http_response.__dict__}" if not status else str(result))
                except Exception as e:
                    service = LogService(get_log_uow_factory())
                    await service.log(
                        ip='ea_notifications',
                        path='ea_notifications',
                        status=False,
                        value='\n'.join(traceback.format_exception(e))
                    )

                elapsed = time.monotonic() - start

                await asyncio.sleep(CYCLE_SECONDS - elapsed)
        except Exception as e:
            service = LogService(get_log_uow_factory())
            await service.log(
                ip='ea_notifications',
                path='ea_notifications',
                status=False,
                value='\n'.join(traceback.format_exception(e))
            )
        finally:
            print("ea_notifications остановлен")
            service = LogService(get_log_uow_factory())
            await service.log(
                ip='ea_notifications',
                path='ea_notifications',
                value="Worker остановлен"
            )

    @classmethod
    async def _process_batch(cls, uow: AppUnitOfWork, rows: list[EAProcessingNotification]) -> list[tuple[str, dict]]:
        """
        Создание уведомлений о скорых внеурочных занятиях

        :return: список параметров уведомлений (firebase-токен, параметры внеурочного занятия)
        """

        if not rows:
            return []

        # Все внеурочные занятия с одинаковым start_time
        start_time = rows[0].start_time
        minutes_left = ceil((start_time - datetime.now(UTC)).total_seconds() / 60)

        # Классы, в которых проходят внеурочные занятия
        groups = {(row.extracurricular_activity.school_id, row.extracurricular_activity.group_id) for row in rows}

        # Сессии детей (и их родителей) в данных классах, у которых включены уведомления
        notifications = await uow.ea_notification_repository.get_notifications(list(groups))

        parents = set()
        sessions_by_class: dict[tuple[int, int], set[tuple[str, int, str]]] = {}  # Сессии, сгруппированные по классам
        profiles: set[tuple[str, int]] = set()  # Пары (session_id, child_id)

        for notification in notifications:
            if notification.session.life:
                key = (notification.child.school_id, notification.child.group_id)
                if sessions_by_class.get(key) is None:
                    sessions_by_class[key] = set()
                sessions_by_class[key].add((notification.session_id, notification.child_id, notification.session.firebase_token))

                profiles.add((notification.session_id, notification.child_id))
                parents.add(notification.session.parent_id)

        # Записи о скрытии внеурочных занятий (для них уведомления не нужны)
        _hidden_ea = await uow.hidden_extracurricular_activity_repository.get_hidden_ea(list(profiles))
        hidden_ea = {(entry.session_id, entry.child_id, entry.subject, entry.place) for entry in _hidden_ea}

        pushes: list[tuple[str, dict]] = []
        processed_ids: list[int] = []

        # Перебор всех скорых внеурочных занятий
        for row in rows:
            activity = row.extracurricular_activity
            key = (activity.school_id, activity.group_id)

            # Все сессии в классе, в котором проводится внеурочное занятие
            sessions = sessions_by_class.get(key, set())

            for session_id, child_id, firebase_token in sessions:
                if (session_id, child_id, activity.subject, activity.place) not in hidden_ea:
                    pushes.append((firebase_token, {
                        "subject": activity.subject,
                        "place": activity.place,
                        "minutes_left": minutes_left,
                        "profile": child_id
                    }))

            processed_ids.append(row.ea_id)

        for ea_id in processed_ids:
            await uow.ea_processing_notification_repository.finish_process(ea_id)

        for parent in parents:
            await uow.statistic_repository.add_statistic(parent, StatName.ea_notifications)

        return pushes

    @classmethod
    async def _dispatch_pushes(cls, pushes: list[tuple[str, dict]]) -> Optional[FCMResult]:
        """Отправка уведомлений"""

        if not pushes:
            return None

        return await send_notifications([Notification(
            firebase_token=firebase_token,
            title="Скоро внеурочное занятие",
            message=f"Через {activity['minutes_left']} мин начнётся {activity['subject']} в {activity['place']}",
            channel=AppNotificationChannel.extracurricular_activities,
            data={
                "from_notification": "ea",
                "profile": str(activity['profile']),
                "buttons": json.dumps([{
                    "text": "Скрыть внеурочную",
                    "action": "hide_extracurricular_activity",
                    "data": {
                        "subject": activity['subject'],
                        "place": activity['place']
                    }
                }])
            }
        ) for firebase_token, activity in pushes])

    def stop(self):
        self._running = False


def add_work(loop: AbstractEventLoop, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient) -> Task:
    worker = ExtracurricularActivityWorker(uow_factory, httpx_client)
    return loop.create_task(worker.run())
