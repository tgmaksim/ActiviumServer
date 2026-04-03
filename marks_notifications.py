import time
import asyncio
import traceback

from yarl import URL
from pathlib import Path
from random import shuffle
from datetime import datetime, UTC
from typing import Callable, Optional

from httpx import AsyncClient
from asyncio import AbstractEventLoop

from PIL.ImageDraw import Draw
from PIL import Image, ImageFont

from firebase.messaging import send_notifications, Notification, AppNotificationChannel

from dnevnikru import AioDnevnikruApi, BaseDnevnikruException

from src.models.child_model import Child
from src.config.project_config import settings
from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory
from src.support.schemas.dnevnik_schemas import MarkLog
from src.support.repositories.app_uow import AppUnitOfWork
from src.models.marks_notification_model import MarksNotification


CYCLE_SECONDS = 10 * 60

__all__ = ['MarksNotificationWorker', 'add_work']


class MarksNotificationWorker:
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        self._running = True
        self.uow_factory = uow_factory
        self.httpx_client = httpx_client

    async def run(self):
        service = LogService(get_log_uow_factory())
        await service.log(
            path='marks_notifications',
            value="Worker запущен"
        )
        print("marks_notifications запущен")

        try:
            while self._running:
                start = time.monotonic()

                children_count = 0

                try:
                    async with self.uow_factory() as uow:
                        children_count = await self._children_count(uow)
                        rows = await self._acquire_child(uow)

                        pushes = await self._process_child(uow, rows)

                        await self._dispatch_pushes(pushes)
                except Exception as e:
                    service = LogService(get_log_uow_factory())
                    await service.log(
                        path='marks_notifications',
                        status=False,
                        value='\n'.join(traceback.format_exception(e))
                    )

                elapsed = time.monotonic() - start
                sleep_time = self._compute_sleep(children_count, elapsed)

                await asyncio.sleep(sleep_time)
        except Exception as e:
            service = LogService(get_log_uow_factory())
            await service.log(
                path='ea_notifications',
                status=False,
                value='\n'.join(traceback.format_exception(e))
            )
        finally:
            print("marks_notifications остановлен")
            service = LogService(get_log_uow_factory())
            await service.log(
                path='marks_notifications',
                value="Worker остановлен"
            )

    @classmethod
    async def _children_count(cls, uow: AppUnitOfWork) -> int:
        """Количество детей, у которых включена функция"""

        return await uow.marks_notification_repository.get_count()

    @classmethod
    async def _acquire_child(cls, uow: AppUnitOfWork) -> list[MarksNotification]:
        """Следующие пользователи, которым нужно отправить уведомление по ребенку"""

        return await uow.marks_notification_repository.get_next_child()

    async def _process_child(self, uow: AppUnitOfWork, rows: list[MarksNotification]) -> list[tuple[str, dict]]:
        """Проверка новых оценок и возвращение необходимых уведомлений"""

        if not rows:
            return []

        # Вся работа для одного ребенка
        child = rows[0].child
        last_mark = rows[0].last_mark

        marks: list[dict] = []

        shuffle(rows)  # Перемешивание для предотвращения частого использования одного dnevnik_token

        for session in map(lambda r: r.session, rows):
            turn_off = not session.life  # Сессия больше не работает

            if not turn_off:
                try:
                    marks = await self.fetch_marks(session.dnevnik_token, child, last_mark)
                except BaseDnevnikruException as e:
                    turn_off = not await uow.session_repository.check_session_auth(session.session_id)  # Выключается сессия, если больше не работает
                    if not turn_off:  # Логирование ошибки
                        await uow.log_repository.add_log(
                            path='marks_notifications',
                            session_id=session.session_id,
                            status=False,
                            value='\n'.join(traceback.format_exception(e))
                        )

            if turn_off:
                await uow.marks_notification_repository.turn_off(session.session_id, child.child_id)
            else:
                continue  # Использование следующей сессии для получения оценок

        pushes = []
        parents = set()
        firebase_tokens = set()

        newest_date = None
        if marks:
            newest_date = max(m['date'] for m in marks)

            for row in rows:
                if row.session.firebase_token not in firebase_tokens:
                    firebase_tokens.add(row.session.firebase_token)
                    parents.add(row.session.parent_id)

                    for mark in marks:
                        pushes.append((row.session.firebase_token, mark))

        await uow.marks_notification_repository.update_date(child.child_id, newest_date)

        for parent in parents:
            await uow.statistic_repository.add_statistic(parent, 'dnevnik_notification')

        return pushes

    async def fetch_marks(self, dnevnik_token: str, child: Child, last_mark: datetime) -> list[dict]:
        """Получение новых оценок ребенка"""

        dnr = AioDnevnikruApi(self.httpx_client, dnevnik_token)

        result = await dnr.get_person_recent_marks(child.child_id, child.group_id, from_date=last_mark)

        works = {work['id']: work for work in result['works']}
        subjects = {subject['id']: subject['name'] for subject in result['subjects']}

        return [{
            'value': mark['textValue'],
            'mood': mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
            'subject': subjects.get(works.get(mark['work'], {}).get('subjectId')),
            'date': date
        } for mark in result['marks'] if (date := datetime.fromisoformat(mark['date']).replace(tzinfo=UTC)) > last_mark]

    async def _dispatch_pushes(self, pushes: list[tuple[str, dict]]):
        """Отправка уведомлений"""

        if not pushes:
            return

        await send_notifications([Notification(
            firebase_token=firebase_token,
            image=self.get_mark_url(mark['value'], mark['mood']),
            title=f"{'🥳 Ура! ' * (mark['mood'] == 'good')}Новая оценка",
            message=f"Вам выставили «{mark['value']}» по предмету {mark['subject']}",
            channel=AppNotificationChannel.marks
        ) for firebase_token, mark in pushes])

    def get_mark_url(self, mark: str, mark_type: str) -> Optional[str]:
        """Ссылка на статический ресурс с картинкой оценки"""

        relative_path = ('marks', f'{mark}.{mark_type}.png')
        path = Path(settings.WWW_PATH, *relative_path)

        if not path.exists():
            bg_colors = {
                'good': '#4B9A25',
                'average': '#FF8F00',
                'bad': '#CF3838'
            }
            bg_color = bg_colors.get(mark_type, '#94ACC8')
            self.create_mark_icon(mark, bg_color, str(path))

        return str(URL(settings.URL).joinpath(*relative_path))

    @staticmethod
    def create_mark_icon(mark: str, bg_color: str, path: str):
        """Создание картинки с оценкой"""

        coefficient = 10

        size = 32 * coefficient
        radius = 5 * coefficient
        font_size = 25 * coefficient

        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = Draw(img)

        draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=bg_color)

        font = ImageFont.truetype("Roboto-Medium.ttf", font_size)

        draw.text((size // 2, size // 2), mark, fill='white', font=font, anchor='mm')

        img.save(path)

    @classmethod
    def _compute_sleep(cls, children_count: int, elapsed: float) -> float:
        interval = CYCLE_SECONDS / max(children_count, 1)
        return max(interval - elapsed, 0)

    def stop(self):
        self._running = False


def add_work(loop: AbstractEventLoop, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
    worker = MarksNotificationWorker(uow_factory, httpx_client)
    return loop.create_task(worker.run())
