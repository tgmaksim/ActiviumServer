import time
import asyncio
import traceback

from yarl import URL
from pathlib import Path
from random import shuffle
from datetime import datetime, UTC
from typing import Callable, Optional

from httpx import AsyncClient
from asyncio import AbstractEventLoop, gather, Task

from PIL.ImageDraw import Draw
from PIL import Image, ImageFont

from firebase.messaging import send_notifications, Notification, AppNotificationChannel, FCMResult

from dnevnikru import AioDnevnikruApi, BaseDnevnikruException

from src.models.child_model import Child
from src.config.project_config import settings
from src.services.log_service import LogService
from src.dependencies.uow import get_log_uow_factory
from src.support.schemas.dnevnik_schemas import MarkLog
from src.repositories.statistic_repository import StatName
from src.support.repositories.app_uow import AppUnitOfWork
from src.models.marks_notification_model import MarksNotification


CYCLE_SECONDS = 10 * 60

__all__ = ['MarksNotificationWorker', 'add_work']


class MarksNotificationWorker:
    """
    Класс для работы уведомлений о новых оценках

    За каждый проход берется один ребенок с включенными уведомлениями,
    у которого дольше всех не проверялись новые оценки. Делается запрос в Дневник.ру для получения последних оценок.
    Если появились новые оценки, то рассылаются уведомления всем сессиям ребенка и его родителей о новых оценках

    Интервал между проходами рассчитывается как CYCLE_SECONDS / (children_count / count_workers), где
    CYCLE_SECONDS - длина цикла (10 минут), children_count - количество детей с включенными уведомлениями,
    count_workers - количество запущенных worker'ов уведомлений. Это позволяет равномерно распределить нагрузку
    """

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        self._running = False
        self.uow_factory = uow_factory
        self.httpx_client = httpx_client

    async def run(self):
        self._running = True

        service = LogService(get_log_uow_factory())
        await service.log(
            ip='marks_notifications',
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
                        # Сессии одного ребенка с включенными уведомлениями для следующей обработки
                        rows = await self._acquire_child(uow)

                        try:
                            # Уведомления, которые нужно отправить
                            pushes, child_id = await self._process_child(uow, rows)

                            # Результат отправки каждого уведомления
                            response = await self._dispatch_pushes(pushes, child_id)

                            for firebase_token, result in (response.results if response else []):
                                status = result.exception is None
                                await uow.log_repository.add_log(
                                    ip='marks_notifications',
                                    path=firebase_token,
                                    status=status,
                                    value=f"{result.exception}: {result.exception.http_response} {result.exception.cause} "
                                          f"{result.exception.http_response.__dict__}" if not status else str(result)
                                )
                        except Exception:
                            # Если произошла ошибка при обработке одного ребенка, то он пропускается:
                            # его дата последне оценки не меняется, но обновляется updated_at
                            await uow.marks_notification_repository.update_date(rows[0].child_id, None)
                            raise
                except Exception as e:
                    service = LogService(get_log_uow_factory())
                    await service.log(
                        ip='marks_notifications',
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
                ip='marks_notifications',
                path='marks_notifications',
                status=False,
                value='\n'.join(traceback.format_exception(e))
            )
        finally:
            print("marks_notifications остановлен")
            service = LogService(get_log_uow_factory())
            await service.log(
                ip='marks_notifications',
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

    async def _process_child(
            self,
            uow: AppUnitOfWork,
            rows: list[MarksNotification]
    ) -> tuple[list[tuple[str, dict, Optional[str]]], Optional[int]]:
        """
        Проверка новых оценок и возвращение необходимых уведомлений

        :return: список параметров для уведомлений
        (firebase-токен, параметры оценки, имя ребенка для уведомлений родителю) и идентификатор ребенка,
        если список rows непустой
        """

        if not rows:
            return [], None

        # Вся работа для одного ребенка
        child = rows[0].child
        last_mark = rows[0].last_mark

        marks: list[dict] = []
        profile: str = ""  # Имя профиля (ребенка)

        shuffle(rows)  # Перемешивание для предотвращения частого использования одного dnevnik_token

        # Берется случайная сессия, которая связана с текущим ребенком (он сам или родитель)
        # Если запрос неуспешный, то берется следующая сессия, пока не будет достигнут результат
        for session in map(lambda r: r.session, rows):
            turn_off = not session.life  # Сессия больше не работает

            if not turn_off:
                try:
                    # Запрашиваются последние оценки и имя ребенка
                    marks, profile = await self.fetch_marks(session.dnevnik_token, child, last_mark)
                    break
                except BaseDnevnikruException as e:
                    # Проверка авторизации сессии в Дневнике.ру
                    turn_off = not await uow.session_repository.check_session_auth(session.session_id)
                    if turn_off:
                        # Выключение сессии
                        await uow.session_repository.kill_session(session.session_id)
                    else:  # Логирование ошибки
                        await uow.log_repository.add_log(
                            ip='marks_notifications',
                            path='marks_notifications',
                            session_id=session.session_id,
                            status=False,
                            value='\n'.join(traceback.format_exception(e))
                        )

            if turn_off:
                # Выключение уведомлений для нерабочей сессии
                await uow.marks_notification_repository.turn_off(session.session_id, child.child_id)

        pushes = []
        parents = set()
        firebase_tokens = set()

        newest_date = None
        if marks:
            newest_date = max(m['date'] for m in marks)

            for row in rows:
                # Если этот firebase-токен еще не добавлен
                if row.session.firebase_token not in firebase_tokens:
                    firebase_tokens.add(row.session.firebase_token)
                    parents.add(row.session.parent_id)
                    _profile = profile if row.session.parent_id != child.child_id else None

                    for mark in marks:
                        # то добавляются уведомления о каждой оценке для этого устройства
                        pushes.append((row.session.firebase_token, mark, _profile))

        # Дата последней оценки обновляется для учета предыдущих оценок в следующий раз
        await uow.marks_notification_repository.update_date(child.child_id, newest_date)

        for parent in parents:
            await uow.statistic_repository.add_statistic(parent, StatName.marks_notifications)

        return pushes, child.child_id

    async def fetch_marks(self, dnevnik_token: str, child: Child, last_mark: datetime) -> tuple[list[dict], str]:
        """
        Получение новых оценок ребенка

        :param dnevnik_token: токен для запросов к Дневнику.ру
        :param child: параметры ребенка
        :param last_mark: время выставления последней обработанной оценки
        :return: список новых оценок и имя ребенка
        """

        dnr = AioDnevnikruApi(self.httpx_client, dnevnik_token)

        # Запрашиваются последние оценки, которые выставлены не ранее прошлой обработанной оценки.
        # В ответе вернутся в том числе последняя обработанная оценка и другие оценки,
        # которые выставлены ровно в это же время
        result, profile = await gather(
            dnr.get_person_recent_marks(child.child_id, child.group_id, from_date=last_mark),
            dnr.get_person(child.child_id)
        )

        works = {work['id']: work for work in result['works']}
        subjects = {subject['id']: subject['name'] for subject in result['subjects']}

        # Игнорируются последняя обработанная в прошлый раз оценка и все оценки, выставленные ровно в это же время
        answer = [{
            'value': mark['textValue'],
            'mood': mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
            'subject': subjects.get(works.get(mark['work'], {}).get('subjectId')),
            'date': date
        } for mark in result['marks'] if (date := datetime.fromisoformat(mark['date']).replace(tzinfo=UTC)) > last_mark]

        return answer, profile['shortName']

    async def _dispatch_pushes(self, pushes: list[tuple[str, dict, Optional[str]]], child_id: Optional[int]) -> Optional[FCMResult]:
        """Отправка уведомлений"""

        if not pushes:
            return None

        return await send_notifications([Notification(
            firebase_token=firebase_token,
            image=self._get_mark_url(mark['value'], mark['mood']),
            title=f"{'🥳 Ура! ' * (mark['mood'] == 'good')}Новая оценка",
            message=(f"{profile}: " if profile else '') +
                    f"Получена оценка «{mark['value']}» по предмету {mark['subject']}",
            channel=AppNotificationChannel.marks,
            data={
                "from_notification": "new_mark",
                "good_mark": str(mark['mood'] == 'good').lower(),
                "profile": child_id
            }
        ) for firebase_token, mark, profile in pushes])

    def _get_mark_url(self, mark: str, mark_type: str) -> Optional[str]:
        """Ссылка на статический ресурс с картинкой оценки"""

        relative_path = ('marks', f'{mark}.{mark_type}.png')
        path = Path(settings.WWW_PATH, *relative_path)

        # Если картинка такой оценки ранее не была создана, то она рисуется
        if not path.exists():
            bg_colors = {
                'good': '#4B9A25',
                'average': '#FF8F00',
                'bad': '#CF3838'
            }
            bg_color = bg_colors.get(mark_type, '#94ACC8')
            self.create_mark_icon(mark, bg_color, str(path))

        # Возвращается ссылка на статический ресурс на сервере
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
        interval = CYCLE_SECONDS / max(children_count / settings.COUNT_MARKS_NOTIFICATIONS_WORKERS, 1)
        return max(interval - elapsed, 0)

    def stop(self):
        self._running = False


def add_work(loop: AbstractEventLoop, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient) -> Task:
    worker = MarksNotificationWorker(uow_factory, httpx_client)
    return loop.create_task(worker.run())
