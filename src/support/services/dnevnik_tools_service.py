import traceback
from asyncio import gather
from datetime import datetime

from httpx import AsyncClient
from typing import Callable, Optional, Union

from ...utils.zip_int import unzip_int
from ...dependencies.auth import check_session

from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi
from dnevnikru.exceptions import BaseDnevnikruException, InvalidResponseException

from firebase.messaging import send_notifications, Notification, AppNotificationChannel

from ..schemas.dnevnik_tools_schemas import (
    Note,
    Note0x34,
    NoteResult,
    NoteResult0x35,
    NoteApiResponse,
    PraiseApiResponse,
    NoteApiResponse0x38,
    DeleteNoteApiResponse,
    PraiseApiResponse0x3A,
    CreateNoteApiResponse,
    CreateNoteApiResponse0x36,
    HighlightPersonApiResponse,
    UnhighlightPersonApiResponse,
)

from ...models.child_model import Child
from ...models.parent_model import Parent
from ...schemas.error_schema import ApiError
from ...api.session_error import SessionError
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ...repositories.statistic_repository import StatName


__all__ = ['DnevnikToolsService']


class DnevnikToolsService(BaseService[AppUnitOfWork]):
    """Сервис для дополнительного взаимодействия с расписанием и оценками"""

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def create_note(self, session_id: str, lesson_key: str, text: str, public: bool, remind_time: Optional[datetime], api: int = None) -> Union[CreateNoteApiResponse0x36, CreateNoteApiResponse]:
        if api == 0:
            answer_type = CreateNoteApiResponse0x36
            result_type = NoteResult0x35
            note_type = Note0x34
        else:
            answer_type = CreateNoteApiResponse
            result_type = NoteResult
            note_type = Note

        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            try:
                lesson_id = unzip_int(lesson_key)
            except (ValueError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='createNote',
                    status=False,
                    session_id=session_id,
                    value=f"lesson_key: {lesson_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Урок не найден"
                    )
                )

            # Если заметка уже создана ребенком (владельцем профиля) и является закрытой
            note = await uow.lesson_note_repository.get_note(child.child_id, lesson_id)
            if note is not None and not note.public and parent.parent_id != child.child_id:
                await uow.log_repository.add_log(
                    path='createNote',
                    session_id=session_id,
                    value=f"Попытка изменить закрытую заметку {lesson_key}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="NoteAccessDeniedError",
                        errorMessage="Заметка на данный урок уже создана ребенком"
                    )
                )

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                await dnr.get_lesson(lesson_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e

                # Если ошибка связана с отсутствием урока в Дневнике.ру
                if not isinstance(e, InvalidResponseException):
                    await uow.log_repository.add_log(
                        path='createNote',
                        session_id=session_id,
                        status=False,
                        value=f"Урок {lesson_id} для создания заметки не найден"
                    )
                    return answer_type(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Урок не найден"
                        )
                    )
                raise

            await uow.lesson_note_repository.create_note(child.child_id, lesson_id, text, public, remind_time)

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.createNote)

            return answer_type(
                answer=result_type(
                    note=note_type(
                        lessonKey=lesson_key,
                        text=text,
                        public=public,
                        remindTime=remind_time  # Для Note0x42 игнорируется
                    )
                )
            )

    async def get_note(self, session_id: str, lesson_key: str, api: int = None) -> Union[NoteApiResponse0x38, NoteApiResponse]:
        if api == 0:
            answer_type = NoteApiResponse0x38
            result_type = NoteResult0x35
            note_type = Note0x34
        else:
            answer_type = NoteApiResponse
            result_type = NoteResult
            note_type = Note

        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            try:
                lesson_id = unzip_int(lesson_key)
            except (ValueError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='getNote',
                    session_id=session_id,
                    status=False,
                    value=f"lesson_key: {lesson_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Урок не найден"
                    )
                )

            note = await uow.lesson_note_repository.get_note(child.child_id, lesson_id)

            # Если заметка уже создана ребенком (владельцем профиля) и является закрытой
            if note is not None and not note.public and parent.parent_id != child.child_id:
                note = None

            return answer_type(
                answer=result_type(
                    note=note_type(
                        lessonKey=lesson_key,
                        text=note.text,
                        public=note.public,
                        remindTime=note.remind_time  # Для Note0x32 игнорируется
                    ) if note else None
                )
            )

    async def delete_note(self, session_id: str, lesson_key: str) -> DeleteNoteApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            try:
                lesson_id = unzip_int(lesson_key)
            except (ValueError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='deleteNote',
                    session_id=session_id,
                    status=False,
                    value=f"lesson_key: {lesson_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return DeleteNoteApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Урок не найден"
                    )
                )

            note = await uow.lesson_note_repository.get_note(child.child_id, lesson_id)

            # Если заметка уже создана ребенком (владельцем профиля) и является закрытой
            if note is not None and not note.public and parent.parent_id != child.child_id:
                note = None

            if note is None:
                return DeleteNoteApiResponse(
                    status=False,
                    error=ApiError(
                        type="NoteNotFoundError",
                        errorMessage="Заметка к уроку не найдена"
                    )
                )

            await uow.lesson_note_repository.delete_note(child.child_id, lesson_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.deleteNote)

            return DeleteNoteApiResponse()

    async def send_praise(self, session_id: str, lesson_key: Optional[str], rating_key: Optional[str], text: Optional[str], api: int = None) -> Union[PraiseApiResponse0x3A, PraiseApiResponse]:
        if api == 0:
            answer_type = PraiseApiResponse0x3A
        else:
            answer_type = PraiseApiResponse

        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent
            child: Child = session.active_child

            # Только по одному идентификатору можно отправить похвалу
            if not (lesson_key is None).__xor__(rating_key is None):
                await uow.log_repository.add_log(
                    path='sendPraise',
                    session_id=session_id,
                    status=False,
                    value=f"{lesson_key} {rating_key}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неизвестный идентификатор оценки"
                    )
                )

            try:
                lesson_id = lesson_key and unzip_int(lesson_key)

                rating_type = rating_key and rating_key[0]
                lesson_id = unzip_int(rating_key[1:]) if rating_type == 'l' else lesson_id
                work_id = unzip_int(rating_key[1:]) if rating_type == 'w' else None
            except (ValueError, IndexError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='sendPraise',
                    session_id=session_id,
                    status=False,
                    value=f"rating_key: {rating_key}\n"
                          f"lesson_key: {lesson_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Урок или работа не найдены"
                    )
                )

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                info, children_relatives, lesson_or_work, marks, subjects = await gather(
                    dnr.get_info(),
                    dnr.get_children_relatives(),
                    dnr.get_lesson(lesson_id) if lesson_id is not None else dnr.get_work(work_id),
                    (
                        dnr.get_person_marks_by_lesson(child.child_id, lesson_id) if lesson_id is not None
                        else dnr.get_person_marks_by_work(child.child_id, work_id)
                    ),
                    dnr.get_subjects(child.group_id)
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e

                # Если ошибка связана с отсутствием урока в Дневнике.ру
                if not isinstance(e, InvalidResponseException):
                    await uow.log_repository.add_log(
                        path='sendPraise',
                        session_id=session_id,
                        status=False,
                        value='\n'.join(traceback.format_exception(e))
                    )
                    return answer_type(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Урок не найден"
                        )
                    )
                raise

            if lesson_id is not None:
                subject = lesson_or_work['subject']['name']
            else:
                subject = None
                for _subject in subjects:
                    if _subject['id'] == lesson_or_work['subjectId']:
                        subject = _subject['name']

            if not marks:
                await uow.log_repository.add_log(
                    path='sendPraise',
                    session_id=session_id,
                    status=False,
                    value=f"Не найдены оценки для похвалы на уроке {lesson_id}"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="NoMarksError",
                        errorMessage="Нет оценок для похвалы"
                    )
                )

            if parent.parent_id == child.child_id:
                await uow.log_repository.add_log(
                    path='sendPraise',
                    session_id=session_id,
                    status=False,
                    value="Попытка отправить похвалу ребенком"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ChildCanNotSendPraiseError",
                        errorMessage="Ребенок не может отправить себе похвалу"
                    )
                )

            child_sessions = await uow.session_repository.get_sessions(child.child_id)  # Все сессии ребенка
            firebase_tokens = {
                child_session.firebase_token
                for child_session in child_sessions
                if child_session.firebase_token is not None
            }

            if not firebase_tokens:
                await uow.log_repository.add_log(
                    path='sendPraise',
                    session_id=session_id,
                    value=f"Ребенок {child.child_id} не имеет активных сессий"
                )
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="NoSessionsError",
                        errorMessage="Ребенок не имеет активных сессий в приложений"
                    )
                )

            message = self._build_praise_text(
                child, parent, info, text, marks, subject, children_relatives
            )

            response = await send_notifications([Notification(
                firebase_token=firebase_token,
                title="😎 Получай похвалу 🥰",
                message=message,
                channel=AppNotificationChannel.praise,
                data={"from_notification": "praise"}
            ) for firebase_token in firebase_tokens])

            # Логирование firebase
            for firebase_token, result in (response.results if response else []):
                status = result.exception is None
                await uow.log_repository.add_log(
                    ip='praise_notifications',
                    path=firebase_token,
                    status=status,
                    value=f"{result.exception}: {result.exception.http_response} {result.exception.cause} "
                          f"{result.exception.http_response.__dict__}" if not status else str(result)
                )

            if response.success_count == 0:
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="SendPraiseError",
                        errorMessage="Произошла ошибка. Попробуйте еще раз или повторите позднее"
                    )
                )

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.sendPraise)

            return answer_type()

    @classmethod
    def _build_praise_text(
            cls,
            child: Child,
            parent: Parent,
            info: dict,
            text: Optional[str],
            marks: list[dict],
            subject: Optional[str],
            children_relatives: list[dict],
    ) -> str:
        """
        Сборка сообщения с похвалой

        :param child: ребенок, которого требуется похвалить
        :param parent: пользователь
        :param info: get_info от Дневника.ру
        :param text: дополнительный текст к похвале от родителя
        :param marks: оценки, за которые отправлена похвала
        :param subject: учебный предмет, по которому получены оценки
        :param children_relatives: родственные связи ребенка для определения отношения к родителю
        :return: полное сообщение с похвалой
        """

        verb = "похвалила" if info['sex'] == 'Female' else "похвалил"
        quote = f": «{text}»".strip() if text else ""
        text_marks = '/'.join([mark['textValue'] for mark in marks])

        parent_name = info['shortName']
        relatives = {
            "Mother": "Мама",
            "Father": "Папа",
            "Grandmother": "Бабушка",
            "Grandfather": "Дедушка",
            "Aunt": "Тетя",
            "Uncle": "Дядя",
            "Tutor": "Опекун",
            "Stepmother": "Мачеха",
            "Stepfather": "Отчим"
        }

        for child_relatives in children_relatives:
            if child_relatives['person']['id'] != child.child_id:
                continue

            for child_relative in child_relatives['relatives']:
                if child_relative['person']['id'] != parent.parent_id:
                    continue

                parent_name = relatives.get(child_relative['type'], parent_name)

        return f"{parent_name} {verb} за «{text_marks}»{f" ({subject})" if subject else ''}{quote}"

    async def highlight_person(self, session_id: str, person_key: str) -> HighlightPersonApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            try:
                person_id = unzip_int(person_key)
            except (ValueError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='highlightPerson',
                    session_id=session_id,
                    status=False,
                    value=f"person_key: {person_key}\n"
                          f"{e.__class__.__name__}: {e}"
                )
                return HighlightPersonApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Одноклассник не найден"
                    )
                )

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                await dnr.get_person(person_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e

                # Если ошибка связана с отсутствием персоны в Дневнике.ру
                if not isinstance(e, InvalidResponseException):
                    await uow.log_repository.add_log(
                        path='highlightPerson',
                        session_id=session_id,
                        status=False,
                        value='\n'.join(traceback.format_exception(e))
                    )
                    return HighlightPersonApiResponse(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Одноклассник не найден"
                        )
                    )
                raise

            await uow.highlighting_person_repository.highlight_person(parent.parent_id, person_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.highlightPerson)

            return HighlightPersonApiResponse()

    async def unhighlight_person(self, session_id: str, person_key: str) -> UnhighlightPersonApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            try:
                person_id = unzip_int(person_key)
            except (ValueError, TypeError) as e:
                await uow.log_repository.add_log(
                    path='unhighlightPerson',
                    session_id=session_id,
                    status=False,
                    value=f"person_key: {person_key}\n"
                          f"{e.__class__.__name__}: {e}")
                return UnhighlightPersonApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Одноклассник не найден"
                    )
                )

            highlighting_person = await uow.highlighting_person_repository.get_highlighting_person(parent.parent_id, person_id)
            if highlighting_person is None:
                await uow.log_repository.add_log(
                    path='unhighlightPerson',
                    session_id=session_id,
                    status=False,
                    value=f"Одноклассник {person_id} не выделен"
                )
                return UnhighlightPersonApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Одноклассник не выделен"
                    )
                )

            await uow.highlighting_person_repository.unhighlight_person(parent.parent_id, person_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.unhighlightPerson)

            return UnhighlightPersonApiResponse()
