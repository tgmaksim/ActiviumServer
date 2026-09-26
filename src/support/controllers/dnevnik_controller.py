from typing import Annotated

from fastapi import APIRouter, Query, Depends

from ..schemas.dnevnik_schemas import (
    MarksApiResponse,
    ScheduleApiResponse,
    MarksFinalApiResponse,
    ScheduleApiResponse0x13,
    MarksRatingStatsApiResponse,
    LessonRatingStatsApiResponse,
    MarksSubjectRatingApiResponse,
    MarksRatingStatsApiResponse0x1B,
)

from ...dependencies.auth import get_session_id
from ..services.dnevnik_service import DnevnikService
from ...dependencies.services import get_dnevnik_service


__all__ = ['router']

router = APIRouter(prefix='/dnevnik', tags=["Dnevnik"])
"""Router группы запросов dnevnik"""


@router.get(
    "/getSchedule/0",
    summary="Получение расписания с оценками",
    description="Получение расписания на несколько дней с домашними заданиями, внеурочными занятиями и "
                "оценками с отметками о посещаемости",
    response_model=ScheduleApiResponse0x13,
    deprecated=True  # Устарела с версии API 1.5.5
)
async def _getSchedule0(
        before: Annotated[int, Query(description="Количество дней расписания до сегодня", ge=0, le=14)],
        after: Annotated[int, Query(description="Количество дней после сегодня", ge=0, le=21)],
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> ScheduleApiResponse0x13:
    return await service.getSchedule(sessionId, before, after, api=0)


@router.get(
    "/getSchedule/1",  # Начиная с версии 1.5.6
    summary="Получение расписания с оценками",
    description="Получение расписания на несколько дней с домашними заданиями, внеурочными занятиями и "
                "оценками с отметками о посещаемости",
    response_model=ScheduleApiResponse
)
async def _getSchedule1(
        before: Annotated[int, Query(description="Количество дней расписания до сегодня", ge=0, le=14)],
        after: Annotated[int, Query(description="Количество дней после сегодня", ge=0, le=21)],
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> ScheduleApiResponse:
    return await service.getSchedule(sessionId, before, after, api=1)


@router.get(
    "/getLessonRatingStats/0",
    summary="Получение дополнительной статистики по оценкам на уроке",
    description="Получение дополнительной статистики по полученным оценкам по предмету в нужный день",
    response_model=LessonRatingStatsApiResponse
)
async def _getLessonRatingStats0(
        ratingKey: Annotated[str, Query(description="Ключ от урока, по которому получить статистику", pattern=r'[0-9a-z]{1,13}\.[0-9a-z]{1,13}\.\d{4}-\d{2}-\d{2}', min_length=9, max_length=38)],
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> LessonRatingStatsApiResponse:
    return await service.getLessonRatingStats(sessionId, ratingKey)


@router.get(
    "/getMarks/0",
    summary="Получение оценок последних и по предметам",
    description="Получение последних оценок по дате выставления и оценок за текущий отчетный период (четверть, семестр)",
    response_model=MarksApiResponse
)
async def _getMarks0(
        last: Annotated[int, Query(description="Число дней, за которое будут запрошены последние по дате выставления оценки", ge=1, le=14)],
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksApiResponse:
    return await service.getMarks(sessionId, last)


@router.get(
    "/getMarkRatingStats/0",
    summary="Получение дополнительной статистики по последней оценке",
    description="Получение оценок в классе за урок и дополнительной статистики по полученной оценке. Устарела с версии API 1.4.0",
    response_model=MarksRatingStatsApiResponse0x1B,
    deprecated=True  # Устарела с версии API 1.4.0
)
async def _getMarkRatingStats0(
        ratingKey: Annotated[str, Query(description="Ключ от последней оценки", pattern=r'[wl][0-9a-z]{1,13}', min_length=2, max_length=14)],
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksRatingStatsApiResponse0x1B:
    return await service.getMarksRatingStats(sessionId, ratingKey, api=0)


@router.get(
    "/getMarkRatingStats/1",  # Начиная с версии API 1.4.0
    summary="Получение дополнительной статистики по последней оценке",
    description="Получение оценок в классе за урок и дополнительной статистики по полученной оценке",
    response_model=MarksRatingStatsApiResponse
)
async def _getMarkRatingStats1(
        ratingKey: Annotated[str, Query(description="Ключ от последней оценки", pattern=r'[wl][0-9a-z]{1,13}', min_length=2, max_length=14)],
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksRatingStatsApiResponse:
    return await service.getMarksRatingStats(sessionId, ratingKey)


@router.get(
    "/getMarksSubjectRating/0",
    summary="Получение общего или предметного рейтинга",
    description="Получение общего или предметного рейтинга в классе с изменением места пользователя",
    response_model=MarksSubjectRatingApiResponse
)
async def _getMarksSubjectRating0(
        ratingKey: Annotated[str, Query(description="Ключ от предмета или общий ключ", pattern=r'(?:[0-9a-z]{1,13}\.)?[0-9a-z]{1,13}', min_length=1, max_length=27)],
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksSubjectRatingApiResponse:
    return await service.getMarksSubjectRating(sessionId, ratingKey)


@router.get(
    "/getFinalMarks/0",
    summary="Получение оценок за период и год",
    description="Получение оценок за отчетный период и итоговые за год",
    response_model=MarksFinalApiResponse
)
async def getFinalMarks0(
        sessionId: str = Depends(get_session_id),
        service: DnevnikService = Depends(get_dnevnik_service)
) -> MarksFinalApiResponse:
    return await service.getFinalMarks(sessionId)
