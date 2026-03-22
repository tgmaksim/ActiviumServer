from asyncio import gather
from typing import Callable
from httpx import AsyncClient

from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi
from dnevnikru.exceptions import BaseDnevnikruException, InvalidResponseException

from firebase.messaging import send_notifications, Notification, AppNotificationChannel

from ..schemas.dnevnik_tools_schemas import (
    Note,
    NoteResult,
    CreateNoteResult,
    NoteApiResponse,
    PraiseApiResponse,
    DeleteNoteApiResponse,
    CreateNoteApiResponse,
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

    async def create_note(self, session_id: str, lesson_key: str, text: str) -> CreateNoteApiResponse:
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

            await uow.lesson_note_repository.create_note(parent.active_child_id, lesson_id, text)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'create_note')

            return CreateNoteApiResponse(
                answer=CreateNoteResult(
                    note=Note(
                        lessonKey=lesson_key,
                        text=text
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
                        text=note.text
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

    async def send_praise(self, session_id: str, lesson_key: str) -> PraiseApiResponse:
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
                info, lesson, marks = await gather(
                    dnr.get_info(),
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
            if not child_sessions:
                return PraiseApiResponse(
                    status=False,
                    error=ApiError(
                        type="NoSessionsError",
                        errorMessage="Ребенок не имеет активных сессий в приложений"
                    )
                )

            verb = "похвалила" if info['sex'] == 'female' else "похвалил"
            text_marks = '/'.join(map(lambda mark: mark['textValue'], marks))

            await send_notifications([Notification(
                firebase_token=child_session.firebase_token,
                title="😎 Получай похвалу 🥰",
                message=f"{info['shortName']} {verb} тебя за «{text_marks}» по предмету {lesson['subject']['name']}",
                channel=AppNotificationChannel.praise
            ) for child_session in child_sessions if child_session.firebase_token is not None])

            await uow.statistic_repository.add_statistic(parent.parent_id, 'send_praise')

            return PraiseApiResponse()
