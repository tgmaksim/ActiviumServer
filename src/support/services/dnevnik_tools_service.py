from asyncio import gather

from httpx import AsyncClient
from typing import Callable, Optional, Union

from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi
from dnevnikru.exceptions import BaseDnevnikruException, InvalidResponseException

from firebase.messaging import send_notifications, Notification, AppNotificationChannel

from ..schemas.dnevnik_tools_schemas import (
    Note,
    NoteResult,
    NoteApiResponse,
    PraiseApiResponse,
    PraiseApiResponse0x3A,
    DeleteNoteApiResponse,
    CreateNoteApiResponse,
    HighlightPersonApiResponse,
    UnhighlightPersonApiResponse,
)

from ...models.parent_model import Parent
from ...models.child_model import Child
from ...api.session_error import SessionError
from ...schemas.error_schema import ApiError
from ...dependencies.auth import check_session
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['DnevnikToolsService']


class DnevnikToolsService(BaseService[AppUnitOfWork]):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def create_note(self, session_id: str, lesson_key: str, text: str, public: bool) -> CreateNoteApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = session.active_child

            try:
                lesson_id = int(lesson_key, 36)
            except ValueError:
                return CreateNoteApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Урок не найден"
                    )
                )

            note = await uow.lesson_note_repository.get_note(child.child_id, lesson_id)
            if note is not None and not note.public and parent.parent_id != child.child_id:
                return CreateNoteApiResponse(
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
                if not isinstance(e, InvalidResponseException):
                    return CreateNoteApiResponse(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Урок не найден"
                        )
                    )
                raise

            await uow.lesson_note_repository.create_note(child.child_id, lesson_id, text, public)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'create_note')

            return CreateNoteApiResponse(
                answer=NoteResult(
                    note=Note(
                        lessonKey=lesson_key,
                        text=text,
                        public=public
                    )
                )
            )

    async def get_note(self, session_id: str, lesson_key: str) -> NoteApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = session.active_child

            try:
                lesson_id = int(lesson_key, 36)
            except ValueError:
                lesson_id = None

            note = await uow.lesson_note_repository.get_note(child.child_id, lesson_id)

            return NoteApiResponse(
                answer=NoteResult(
                    note=Note(
                        lessonKey=lesson_key,
                        text=note.text,
                        public=note.public
                    ) if note else None
                )
            )

    async def delete_note(self, session_id: str, lesson_key: str) -> DeleteNoteApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = session.active_child

            try:
                lesson_id = int(lesson_key, 36)
            except ValueError:
                lesson_id = None

            note = await uow.lesson_note_repository.get_note(child.child_id, lesson_id)
            if note is None:
                return DeleteNoteApiResponse(
                    status=False,
                    error=ApiError(
                        type="NoteNotFoundError",
                        errorMessage="Заметка к уроку не найдена"
                    )
                )

            await uow.lesson_note_repository.delete_note(child.child_id, lesson_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'delete_note')

            return DeleteNoteApiResponse()

    async def send_praise(self, session_id: str, lesson_key: Optional[str], rating_key: Optional[str], text: Optional[str], api: int = None) -> Union[PraiseApiResponse0x3A, PraiseApiResponse]:
        if api == 0:
            answer_type = PraiseApiResponse0x3A
        else:
            answer_type = PraiseApiResponse

        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent
            child: Child = session.active_child

            if not (lesson_key is None).__xor__(rating_key is None):
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Неизвестный идентификатор оценки"
                    )
                )

            try:
                lesson_id = int(lesson_key, 36) if lesson_key is not None else None
                lesson_id = int(rating_key[1:], 36) if rating_key is not None and rating_key[0] == 'l' else lesson_id
                work_id = int(rating_key[1:], 36) if rating_key is not None and rating_key[0] == 'w' else None
            except ValueError:
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Урок или работа не найдены"
                    )
                )

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                info, children_relatives, lesson_or_work, marks = await gather(
                    dnr.get_info(),
                    dnr.get_children_relatives(),
                    dnr.get_lesson(lesson_id) if lesson_id is not None else dnr.get_work(work_id),
                    dnr.get_person_marks_by_lesson(child.child_id, lesson_id) if lesson_id is not None
                    else dnr.get_person_marks_by_work(child.child_id, work_id)
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                if not isinstance(e, InvalidResponseException):
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
                for _subject in await dnr.get_subjects(child.group_id):
                    if _subject['id'] == lesson_or_work['subjectId']:
                        subject = _subject['name']

            if not marks:
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="NoMarksError",
                        errorMessage="Нет оценок для похвалы"
                    )
                )

            if parent.parent_id == child.child_id:
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="ChildCanNotSendPraiseError",
                        errorMessage="Ребенок не может отправить себе похвалу"
                    )
                )

            child_sessions = await uow.session_repository.get_sessions(child.child_id)
            firebase_tokens = {child_session.firebase_token for child_session in child_sessions if child_session.firebase_token is not None}
            if not firebase_tokens:
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="NoSessionsError",
                        errorMessage="Ребенок не имеет активных сессий в приложений"
                    )
                )

            verb = "похвалила" if info['sex'] == 'Female' else "похвалил"
            quote = f": «{text}»".strip() if text else ""
            text_marks = '/'.join(map(lambda mark: mark['textValue'], marks))

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

            response = await send_notifications([Notification(
                firebase_token=firebase_token,
                title="😎 Получай похвалу 🥰",
                message=f"{parent_name} {verb} за «{text_marks}»{f" ({subject})" if subject else ''}{quote}",
                channel=AppNotificationChannel.praise,
                data={"from_notification": "praise"}
            ) for firebase_token in firebase_tokens])

            for message in response.responses:
                status = message.exception is not None
                await uow.log_repository.add_log(
                    ip='praise_notifications',
                    path='praise_notifications',
                    status=status,
                    value=f"{message.exception}: {message.exception.code} {message.exception.cause} "
                          f"{message.exception.http_response.__dict__}" if status else message.message_id
                )

            if response.success_count == 0:
                return answer_type(
                    status=False,
                    error=ApiError(
                        type="SendPraiseError",
                        errorMessage="Произошла ошибка. Попробуйте еще раз или повторите позднее"
                    )
                )

            await uow.statistic_repository.add_statistic(parent.parent_id, 'send_praise')

            return answer_type()

    async def highlight_person(self, session_id: str, person_key: str) -> HighlightPersonApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            try:
                person_id = int(person_key, 36)
            except ValueError as e:
                await uow.log_repository.add_log(path='highlightPerson', session_id=session_id, status=False,
                                                 value=f"{e.__class__.__name__}: {e}")
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
                return HighlightPersonApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Одноклассник не найден"
                    )
                )

            await uow.highlighting_person_repository.highlight_person(parent.parent_id, person_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'highlight_person')

            return HighlightPersonApiResponse()

    async def unhighlight_person(self, session_id: str, person_key: str) -> UnhighlightPersonApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            try:
                person_id = int(person_key, 36)
            except ValueError as e:
                await uow.log_repository.add_log(path='unhighlightPerson', session_id=session_id, status=False,
                                                 value=f"{e.__class__.__name__}: {e}")
                return UnhighlightPersonApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Одноклассник не найден"
                    )
                )

            highlighting_person = await uow.highlighting_person_repository.get_highlighting_person(parent.parent_id, person_id)
            if highlighting_person is None:
                return UnhighlightPersonApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Одноклассник не найден"
                    )
                )

            await uow.highlighting_person_repository.unhighlight_person(parent.parent_id, person_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'unhighlight_person')

            return UnhighlightPersonApiResponse()
