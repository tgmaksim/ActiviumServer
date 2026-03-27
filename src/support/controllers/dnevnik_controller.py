from typing import Annotated

from fastapi import APIRouter, Query, Depends, Header, Request

from ..schemas.dnevnik_schemas import (
    MarksApiResponse,
    ScheduleApiResponse,
    MarksFinalApiResponse,
    MarksRatingStatsApiResponse,
    LessonRatingStatsApiResponse,
    MarksSubjectRatingApiResponse
)

from ..services.dnevnik_service import DnevnikService
from ...dependencies.services import get_dnevnik_service


__all__ = ['router']

router = APIRouter(prefix='/dnevnik', tags=["Dnevnik"])


@router.get(
    "/getSchedule/0",
    summary="Получение расписания с оценками",
    description="Получение расписания на несколько дней с домашними заданиями, внеурочными занятиями и "
                "оценками с отметками о посещаемости",
    response_model=ScheduleApiResponse
)
async def _getSchedule0(
        request: Request,
        before: Annotated[int, Query(description="Количество дней расписания до сегодня", ge=0, le=14)],
        after: Annotated[int, Query(description="Количество дней после сегодня", ge=0, le=21)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikService = Depends(get_dnevnik_service)
) -> ScheduleApiResponse:
    request.state.session_id = sessionId
    return await service.getSchedule(sessionId, before, after)


@router.get(
    "/getLessonRatingStats/0",
    summary="Получение дополнительной статистики по оценкам на уроке",
    description="Получение дополнительной статистики по полученным оценкам по предмету в нужный день",
    response_model=LessonRatingStatsApiResponse
)
async def _getLessonRatingStats0(
        request: Request,
        ratingKey: Annotated[str, Query(description="Ключ от урока, по которому получить статистику", pattern=r'[0-9a-z]{1,13}\.[0-9a-z]{1,13}\.\d{4}-\d{2}-\d{2}', min_length=9, max_length=38)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikService = Depends(get_dnevnik_service)
) -> LessonRatingStatsApiResponse:
    request.state.session_id = sessionId
    return await service.getLessonRatingStats(sessionId, ratingKey)


@router.get(
    "/getMarks/0",
    summary="Получение оценок последних и по предметам",
    description="Получение последних оценок по дате выставления и оценок за текущий отчетный период (четверть, семестр)",
    response_model=MarksApiResponse
)
async def _getMarks0(
        request: Request,
        last: Annotated[int, Query(description="Число дней, за которое будут запрошены последние по дате выставления оценки", ge=1, le=7)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksApiResponse:
    request.state.session_id = sessionId
    return await service.getMarks(sessionId, last)


@router.get(
    "/getMarkRatingStats/0",
    summary="Получение дополнительной статистики по последней оценке",
    description="Получение оценок в классе за урок и дополнительной статистики по полученной оценке",
    response_model=MarksRatingStatsApiResponse
)
async def _getMarkRatingStats0(
        request: Request,
        ratingKey: Annotated[str, Query(description="Ключ от последней оценки", pattern=r'[wl][0-9a-z]{1,13}', min_length=2, max_length=14)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksRatingStatsApiResponse:
    request.state.session_id = sessionId
    return await service.getMarksRatingStats(sessionId, ratingKey)


@router.get(
    "/getMarksSubjectRating/0",
    summary="Получение общего или предметного рейтинга",
    description="Получение общего или предметного рейтинга в классе с изменением места пользователя",
    response_model=MarksSubjectRatingApiResponse
)
async def _getMarksSubjectRating0(
        request: Request,
        ratingKey: Annotated[str, Query(description="Ключ от предмета или общий ключ", pattern=r'(?:[0-9a-z]{1,13}\.)?[0-9a-z]{1,13}', min_length=1, max_length=27)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksSubjectRatingApiResponse:
    request.state.session_id = sessionId
    return await service.getMarksSubjectRating(sessionId, ratingKey)


@router.get(
    "/getFinalMarks/0",
    summary="Получение оценок за период и год",
    description="Получение оценок за отчетный период и итоговые за год",
    response_model=MarksFinalApiResponse
)
async def getFinalMarks0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksFinalApiResponse:
    request.state.session_id = sessionId
    return await service.getFinalMarks(sessionId)
