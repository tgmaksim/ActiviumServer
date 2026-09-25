import json
import time
import asyncio

from yarl import URL
from pathlib import Path
from random import shuffle
from typing import Callable, Optional
from datetime import datetime, UTC, date

from httpx import AsyncClient
from asyncio import AbstractEventLoop, gather, Task

from PIL.ImageDraw import Draw
from PIL import Image, ImageFont

from backgrounds.base_background import BaseBackground

from firebase.messaging import send_notifications, Notification, AppNotificationChannel, FCMResult

from src.models import Session
from src.utils.cache import CacheService

from src.utils.exception import format_exception

from dnevnikru import AioDnevnikruApi, BaseDnevnikruException

from src.utils.zip_int import zip_int
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


class MarksNotificationWorker(BaseBackground):
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
        super().__init__(uow_factory, httpx_client)
        self.log_service = LogService(get_log_uow_factory())

    @classmethod
    def name(cls) -> str:
        return 'marks_notifications'

    async def run(self):
        async with self.run_context():
            while self._running:
                start = time.monotonic()

                children_count = 0

                rows: list[MarksNotification] = []
                try:
                    async with self.uow_factory() as uow:
                        children_count = await self._children_count(uow)
                        # Сессии одного ребенка с включенными уведомлениями для следующей обработки
                        rows = await self._acquire_child(uow)

                        # Уведомления, которые нужно отправить
                        pushes_for_new_marks, pushes_for_deleted_marks, pushes_for_updated_marks, child_id = \
                            await self._process_child(uow, rows)

                    # Результат отправки каждого уведомления
                    response = await self._dispatch_pushes(
                        pushes_for_new_marks, pushes_for_deleted_marks, pushes_for_updated_marks, child_id)

                    # Обработка результатов отправленных уведомлений
                    await self.process_pushes(response)
                except Exception as e:
                    if len(rows) > 0:
                        # Если произошла ошибка при обработке одного ребенка, то он пропускается:
                        # обновляется его updated_at
                        async with self.uow_factory() as uow:
                            await uow.marks_notification_repository.update_date(rows[0].child_id)

                    await self.log_service.log(
                        ip=self.name(),
                        path=self.name(),
                        status=False,
                        value=format_exception(e)
                    )

                elapsed = time.monotonic() - start
                sleep_time = self._compute_sleep(children_count, elapsed)

                await asyncio.sleep(sleep_time)

    @classmethod
    async def _children_count(cls, uow: AppUnitOfWork) -> int:
        """Количество детей, у которых включена функция"""

        return await uow.marks_notification_repository.get_count()

    @classmethod
    async def _acquire_child(cls, uow: AppUnitOfWork) -> list[MarksNotification]:
        """Следующие пользователи, которым нужно отправить уведомление по ребенку"""

        return await uow.marks_notification_repository.get_next_child()

    async def _process_child(self, uow: AppUnitOfWork, rows: list[MarksNotification]) -> tuple[
        list[tuple[str, dict, Optional[str]]],
        list[tuple[str, dict, Optional[str]]],
        list[tuple[str, dict, Optional[str]]],
        Optional[int]
    ]:
        """
        Проверка новых оценок и возвращение необходимых уведомлений

        :return: список параметров для уведомлений
        (firebase-токен, параметры оценки, имя ребенка для уведомлений родителю) и идентификатор ребенка,
        если список rows непустой
        """

        if not rows:
            return [], [], [], None

        # Чаще всего updated_at у всех одинаковый, но для избежания ошибок
        # для получения обработанных оценок используется самый обновленный
        main_row = max(rows, key=lambda r: r.updated_at)

        child = main_row.child  # Вся работа для одного ребенка

        current_marks = main_row.marks
        current_marks_hash = main_row.marks_hash
        current_period_id = main_row.active_period_id

        marks: list[dict] = []
        new_marks: list[dict] = []
        deleted_marks: list[dict] = []
        updated_marks: list[dict] = []

        profile: str = ""  # Имя профиля (ребенка)
        period: Optional[dict] = None

        shuffle(rows)  # Перемешивание для предотвращения частого использования одного dnevnik_token

        # Берется случайная сессия, которая связана с текущим ребенком (он сам или родитель)
        # Если запрос неуспешный, то берется следующая сессия, пока не будет достигнут результат
        for session in map(lambda r: r.session, rows):
            turn_off = not session.life  # Сессия больше не работает

            if not turn_off:
                dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

                try:
                    if period is None:
                        # Запрашивается текущий отчетный период (из кэша или от Дневника.ру)
                        period = await CacheService.get_period(uow.cache_repository, dnr, main_row.session, child, datetime.now(UTC).date())

                    # Запрашиваются все оценки и имя ребенка
                    marks, new_marks, deleted_marks, updated_marks, profile = await self.fetch_marks(
                        uow, dnr, session, child, period['start'], period['finish'], period['id'],
                        current_marks, current_marks_hash, current_period_id
                    )
                except BaseDnevnikruException as e:
                    # Проверка авторизации сессии в Дневнике.ру
                    turn_off = not await uow.session_repository.check_session_auth(session.session_id)
                    if turn_off:
                        # Выключение сессии
                        await uow.session_repository.kill_session(session.session_id)
                    else:  # Логирование ошибки
                        await self.log_service.log(
                            ip=self.name(),
                            path=self.name(),
                            session_id=session.session_id,
                            status=False,
                            value=format_exception(e)
                        )
                else:
                    break

            # Уведомления остаются включенными. После повторной авторизации сессии продолжают работать
            # if turn_off:
            #     # Выключение уведомлений для нерабочей сессии
            #     await uow.marks_notification_repository.turn_off(session.session_id, child.child_id)

        pushes_for_new_marks: list[tuple[str, dict, Optional[str]]] = []
        pushes_for_deleted_marks: list[tuple[str, dict, Optional[str]]] = []
        pushes_for_updated_marks: list[tuple[str, dict, Optional[str]]] = []

        parents = set()
        firebase_tokens = set()

        if pushes_for_new_marks or pushes_for_deleted_marks or pushes_for_updated_marks:
            for row in rows:
                # Если сессия рабочая и этот firebase-токен еще не добавлен
                if row.session.life and row.session.firebase_token not in firebase_tokens:
                    firebase_tokens.add(row.session.firebase_token)
                    parents.add(row.session.parent_id)

                    _profile = profile if row.session.parent_id != child.child_id else None

                    # то добавляются уведомления о каждой оценке для этого устройства
                    for mark in new_marks:
                        pushes_for_new_marks.append((row.session.firebase_token, mark, _profile))
                    for mark in deleted_marks:
                        pushes_for_deleted_marks.append((row.session.firebase_token, mark, _profile))
                    for mark in updated_marks:
                        pushes_for_updated_marks.append((row.session.firebase_token, mark, _profile))

        # Дата последней оценки обновляется для учета предыдущих оценок в следующий раз
        await uow.marks_notification_repository.update_marks(child.child_id, period['id'], marks)

        for parent in parents:
            await uow.statistic_repository.add_statistic(parent, StatName.marks_notifications)

        return pushes_for_new_marks, pushes_for_deleted_marks, pushes_for_updated_marks, child.child_id

    @classmethod
    async def fetch_marks(
            cls,
            uow: AppUnitOfWork, dnr: AioDnevnikruApi, session: Session, child: Child,
            from_date: date, to_date: date, period_id: int,
            current_marks: list[dict], current_marks_hash: str, current_period_id: int
    ) -> tuple[list[dict], list[dict], list[dict], list[dict], str]:
        """
        Получение всех, новых, удаленных и измененных оценок ребенка за период

        :param uow: AppUnitOfWork для взаимодействия с БД
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: параметры ребенка
        :param from_date: начало периода
        :param to_date: конец периода
        :param period_id: идентификатор текущего отчетного периода
        :param current_marks: обработанные оценки
        :param current_marks_hash: хэш обработанных оценок
        :param current_period_id: идентификатор отчетного периода, в котором были обработаны оценки
        :return: список оценок и имя ребенка
        """

        # Если идентификаторы текущего периода и обработанного различаются, то прошлые оценки не учитываются
        if period_id != current_period_id:
            current_marks = []
            current_marks_hash = uow.marks_notification_repository.hash_marks(current_marks)

        # Запрашиваются все оценки ребенка за период
        result, _subjects, profile = await gather(
            dnr.get_person_marks(child.child_id, child.group_id, from_date, to_date),
            CacheService.get_subjects(uow.cache_repository, dnr, session, child),
            dnr.get_person(child.child_id)
        )

        subjects = {subject['id']: subject['name'] for subject in _subjects}

        # После миграции БД, но до первой проверки оценок active_period_id = null.
        # Нужно обновить текущие оценки и пропустить
        if current_period_id is None:
            return result, [], [], [], profile['shortName']

        # Если хэш совпадает, то изменений в оценках нет
        if uow.marks_notification_repository.hash_marks(result) == current_marks_hash:
            return result, [], [], [], profile['shortName']

        result_by_id = {mark['id']: mark for mark in result}
        set_result = set(result_by_id.keys())
        current_marks_by_id = {mark['id']: mark for mark in current_marks}
        set_current_marks = set(current_marks_by_id.keys())

        new_marks: list[dict] = []
        deleted_marks: list[dict] = []
        updated_marks: list[dict] = []

        # Новые оценки
        if difference := set_result.difference(set_current_marks):
            new_marks = await cls.create_mark_list(uow, dnr, session, child, result, subjects, difference, result_by_id)

        # Удаленные оценки
        if difference := set_current_marks.difference(set_result):
            deleted_marks = await cls.create_mark_list(uow, dnr, session, child, result, subjects, difference, current_marks_by_id)

        # Измененные оценки
        difference = {
            mark_id
            for mark_id in set_result & set_current_marks
            if result_by_id[mark_id]['value'] != current_marks_by_id[mark_id]['value']
        }
        if difference:
            updated_marks = await cls.create_mark_list(
                uow, dnr, session, child, result, subjects, difference, result_by_id, current_marks_by_id)

        return result, new_marks, deleted_marks, updated_marks, profile['shortName']

    @classmethod
    async def create_mark_list(cls,
            uow: AppUnitOfWork, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            result: list[dict], subjects: dict[int, str],
            ids: set[int], marks_by_id: dict[int, dict], old_marks: dict[int, dict] = None
    ) -> list[dict]:
        if old_marks is None:
            old_marks = {}

        work_types, works = await cls._get_works(uow, dnr, session, child, result)

        return [
            {
                'value': mark['textValue'],
                'oldValue': old_marks.get(mark_id, {}).get('textValue'),
                'mood': mark['mood'].lower() if mark['mood'].lower() in MarkLog.moods else MarkLog.default_mood(),
                'subject': subjects.get(works.get(mark['work'], {}).get('subjectId')),
                'date': datetime.fromisoformat(mark['date']).replace(tzinfo=UTC),
                'work': work_types.get(mark['workType']),
                'ratingKey': f"l{zip_int(mark['lesson'])}" if mark.get('lesson') is not None else f"w{zip_int(mark['work'])}"
            }
            for mark_id in ids if (mark := marks_by_id.get(mark_id))
        ]

    @classmethod
    async def _get_works(
            cls,
            uow: AppUnitOfWork, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            result: list[dict]
    ) -> tuple[dict[int, str], dict[int, dict]]:
        work_types_ids: set[int] = {mark['workType'] for mark in result}
        works_ids: list[int] = [mark['work'] for mark in result]

        _work_types, _works = await gather(
            CacheService.get_work_types(uow.cache_repository, dnr, session, child, work_types_ids),
            dnr.get_works(works_ids)
        )

        works = {work['id']: work for work in _works}
        work_types = {work_type_id: work_type.title for work_type_id, work_type in _work_types.items()}

        return work_types, works

    async def _dispatch_pushes(
            self,
            pushes_for_new_marks: list[tuple[str, dict, Optional[str]]],
            pushes_for_deleted_marks: list[tuple[str, dict, Optional[str]]],
            pushes_for_updated_marks: list[tuple[str, dict, Optional[str]]],
            child_id: Optional[int]
    ) -> Optional[FCMResult]:
        """Отправка уведомлений"""

        notifications: list[Notification] = []

        notifications.extend(
            [
                Notification(
                    firebase_token=firebase_token,
                    image=self._get_mark_url(mark['value'], mark['mood']),
                    title=f"{'🥳 Ура! ' * (mark['mood'] == 'good')}Новая оценка" if mark['oldValue'] is None else "✏️ Оценка изменена",
                    message=(f"{profile}: " * (profile is not None)) +
                            (f"Получена оценка «{mark['value']}»" if mark['oldValue'] is None
                             else f"Изменена оценка с «{mark['oldValue']}» на «{mark['value']}»") +
                            (f" по предмету {mark['subject']}" * (mark['subject'] is not None)) +
                            (f" ({mark['work']})" * (mark['work'] is not None)),
                    channel=AppNotificationChannel.marks,
                    data={
                        "from_notification": "new_mark",
                        "good_mark": str(mark['mood'] == 'good').lower(),
                        "profile": str(child_id),
                        "buttons": json.dumps([{
                            "text": "Отправить похвалу",
                            "action": "praise",
                            "data": {
                                "ratingKey": mark['ratingKey']
                            }
                        }] if profile else [])  # Похвала только для родителей
                    }
                )
                for firebase_token, mark, profile in pushes_for_new_marks + pushes_for_updated_marks
            ]
        )

        notifications.extend(
            [
                Notification(
                    firebase_token=firebase_token,
                    title="🗑 Удалена оценка",
                    message=(f"{profile}: " * (profile is not None)) +
                            f"Удалена оценка «{mark['value']}»" +
                            (f" по предмету {mark['subject']}" * (mark['subject'] is not None)) +
                            (f" ({mark['work']})" * (mark['work'] is not None)),
                    channel=AppNotificationChannel.marks
                )
                for firebase_token, mark, profile in pushes_for_deleted_marks
            ]
        )

        return await send_notifications(notifications)

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

        font_file = Path(settings.RESOURCES_PATH, "Roboto-Medium.ttf")
        font = ImageFont.truetype(font_file, font_size)

        draw.text((size // 2, size // 2), mark, fill='white', font=font, anchor='mm')

        img.save(path)

    @classmethod
    def _compute_sleep(cls, children_count: int, elapsed: float) -> float:
        interval = CYCLE_SECONDS / max(children_count / settings.COUNT_MARKS_NOTIFICATIONS_WORKERS, 1)
        return max(interval - elapsed, 0)


def add_work(loop: AbstractEventLoop, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient) -> Task:
    worker = MarksNotificationWorker(uow_factory, httpx_client)
    return loop.create_task(worker.run())
