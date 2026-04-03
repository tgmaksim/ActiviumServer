from typing import Annotated, Optional

from fastapi import APIRouter, Query, Depends, Body, Request, Header

from ..schemas.dnevnik_tools_schemas import (
    NoteApiResponse,
    PraiseApiResponse,
    DeleteNoteApiResponse,
    CreateNoteApiResponse,
    HighlightPersonApiResponse,
    UnhighlightPersonApiResponse
)

from ..services.dnevnik_tools_service import DnevnikToolsService
from ...dependencies.services import get_dnevnik_tools_service


__all__ = ['router']

router = APIRouter(prefix='/dtools', tags=["Dnevnik Tools"])


@router.post(
    "/createNote/0",
    summary="Создание или изменение заметки",
    description="Создание или изменение текстовой заметки к уроку. Синхронизируется с родителем",
    response_model=CreateNoteApiResponse
)
async def _createNote0(
        request: Request,
        lessonKey: Annotated[str, Query(description="Ключ от урока, к которому нужно создать заметку", pattern=r'[0-9a-z]{1,13}', min_length=1, max_length=13)],
        text: Annotated[str, Body(media_type='plain/text', description="Текст заметки", min_length=1, max_length=128)],
        public: Annotated[bool, Query(description="Заметка доступна родителю")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikToolsService = Depends(get_dnevnik_tools_service)
) -> CreateNoteApiResponse:
    request.state.session_id = sessionId
    return await service.create_note(sessionId, lessonKey, text, public)


@router.get(
    "/getNote/0",
    summary="Получение заметки к уроку",
    description="Получение текстовой заметки к уроку",
    response_model=NoteApiResponse
)
async def _getNote0(
        request: Request,
        lessonKey: Annotated[str, Query(description="Ключ от урока, к которому нужно создать заметку", pattern=r'[0-9a-z]{1,13}', min_length=1, max_length=13)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikToolsService = Depends(get_dnevnik_tools_service)
) -> NoteApiResponse:
    request.state.session_id = sessionId
    return await service.get_note(sessionId, lessonKey)


@router.delete(
    "/deleteNote/0",
    summary="Удаление заметки к уроку",
    description="Удаление текстовой заметки к уроку",
    response_model=DeleteNoteApiResponse
)
async def _deleteNote0(
        request: Request,
        lessonKey: Annotated[str, Query(description="Ключ от урока, к которому нужно создать заметку", pattern=r'[0-9a-z]{1,13}', min_length=1, max_length=13)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikToolsService = Depends(get_dnevnik_tools_service)
) -> DeleteNoteApiResponse:
    request.state.session_id = sessionId
    return await service.delete_note(sessionId, lessonKey)


@router.post(
    "/sendPraise/0",
    summary="Отправка похвалы ребенку от родителя",
    description="Отправка похвалы активному ребенку от родителя на полученные оценки",
    response_model=PraiseApiResponse
)
async def _sendPraise0(
        request: Request,
        lessonKey: Annotated[str, Query(description="Ключ от урока, по которому нужно отправить похвалу", pattern=r'[0-9a-z]{1,13}', min_length=1, max_length=13)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        text: Annotated[Optional[str], Body(media_type="plain/text", description="Короткое сообщение ребенку", min_length=1, max_length=64)] = None,
        service: DnevnikToolsService = Depends(get_dnevnik_tools_service)
) -> PraiseApiResponse:
    request.state.session_id = sessionId
    return await service.send_praise(sessionId, lessonKey, text)


@router.post(
    "/highlightPerson/0",
    summary="Выделение одноклассника в рейтингах",
    description="Выделение одноклассника во всех рейтингах и списках других оценок. Такой одноклассник будет выше других, "
                "но сохранится номер его реального места в рейтингах",
    response_model=HighlightPersonApiResponse
)
async def _highlightPerson0(
        request: Request,
        personKey: Annotated[str, Query(description="Ключ от одноклассника, которого нужно выделить", pattern=r'[0-9a-z]{1,13}', min_length=1, max_length=13)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikToolsService = Depends(get_dnevnik_tools_service)
) -> HighlightPersonApiResponse:
    request.state.session_id = sessionId
    return await service.highlight_person(sessionId, personKey)


@router.post(
    "/unhighlightPerson/0",
    summary="Отмена выделения одноклассника в рейтингах",
    description="Отмена ранее включенного выделения одноклассника в рейтингах. "
                "После отключения его положения будет зависеть только от оценок",
    response_model=UnhighlightPersonApiResponse
)
async def _unhighlightPerson0(
        request: Request,
        personKey: Annotated[str, Query(description="Ключ от одноклассника, у которого нужно выключить выделение", pattern=r'[0-9a-z]{1,13}', min_length=1, max_length=13)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikToolsService = Depends(get_dnevnik_tools_service)
) -> UnhighlightPersonApiResponse:
    request.state.session_id = sessionId
    return await service.unhighlight_person(sessionId, personKey)
