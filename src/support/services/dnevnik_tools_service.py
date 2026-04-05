from asyncio import gather

from asyncpg import UniqueViolationError
from httpx import AsyncClient
from typing import Callable, Optional

from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi
from dnevnikru.exceptions import BaseDnevnikruException, InvalidResponseException

from firebase.messaging import send_notifications, Notification, AppNotificationChannel

from ..schemas.dnevnik_tools_schemas import (
    Note,
    NoteResult,
    NoteApiResponse,
    PraiseApiResponse,
    DeleteNoteApiResponse,
    CreateNoteApiResponse,
    HighlightPersonApiResponse,
    UnhighlightPersonApiResponse
)

from ...models.parent_model import Parent
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

            note = await uow.lesson_note_repository.get_note(parent.active_child_id, lesson_id)
            if note is not None and not note.public and parent.parent_id != parent.active_child_id:
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

            await uow.lesson_note_repository.create_note(parent.active_child_id, lesson_id, text, public)

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

            try:
                lesson_id = int(lesson_key, 36)
            except ValueError:
                lesson_id = None

            note = await uow.lesson_note_repository.get_note(parent.active_child_id, lesson_id)

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

            try:
                lesson_id = int(lesson_key, 36)
            except ValueError:
                lesson_id = None

            note = await uow.lesson_note_repository.get_note(parent.active_child_id, lesson_id)
            if note is None:
                return DeleteNoteApiResponse(
                    status=False,
                    error=ApiError(
                        type="NoteNotFoundError",
                        errorMessage="Заметка к уроку не найдена"
                    )
                )

            await uow.lesson_note_repository.delete_note(parent.active_child_id, lesson_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'delete_note')

            return DeleteNoteApiResponse()

    async def send_praise(self, session_id: str, lesson_key: str, text: Optional[str]) -> PraiseApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            try:
                lesson_id = int(lesson_key, 36)
            except ValueError:
                return PraiseApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Урок не найден"
                    )
                )

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                info, children_relatives, lesson, marks = await gather(
                    dnr.get_info(),
                    dnr.get_children_relatives(),
                    dnr.get_lesson(lesson_id),
                    dnr.get_person_marks_by_lesson(parent.active_child_id, lesson_id)
                )
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                if not isinstance(e, InvalidResponseException):
                    return PraiseApiResponse(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Урок не найден"
                        )
                    )
                raise

            if not marks:
                return PraiseApiResponse(
                    status=False,
                    error=ApiError(
                        type="NoMarksError",
                        errorMessage="Нет оценок для похвалы"
                    )
                )

            if parent.parent_id == parent.active_child_id:
                return PraiseApiResponse(
                    status=False,
                    error=ApiError(
                        type="ChildCanNotSendPraiseError",
                        errorMessage="Ребенок не может отправить себе похвалу"
                    )
                )

            child_sessions = await uow.session_repository.get_sessions(parent.active_child_id)
            firebase_tokens = {child.firebase_token for child in child_sessions if child.firebase_token is not None}
            if not firebase_tokens:
                return PraiseApiResponse(
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
                if child_relatives['person']['id'] != parent.active_child_id:
                    continue

                for child_relative in child_relatives['relatives']:
                    if child_relative['person']['id'] != parent.parent_id:
                        continue

                    parent_name = relatives.get(child_relative['type'], parent_name)

            await send_notifications([Notification(
                firebase_token=firebase_token,
                title="😎 Получай похвалу 🥰",
                message=f"{parent_name} {verb} за «{text_marks}» ({lesson['subject']['name']}){quote}",
                channel=AppNotificationChannel.praise
            ) for firebase_token in firebase_tokens])

            await uow.statistic_repository.add_statistic(parent.parent_id, 'send_praise')

            return PraiseApiResponse()

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

            try:
                await uow.highlighting_person_repository.highlight_person(parent.parent_id, person_id)
            except UniqueViolationError:
                pass

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

            return UnhighlightPersonApiResponse()
