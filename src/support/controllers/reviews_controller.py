from typing import Annotated, Optional, Literal

from fastapi.params import Header
from fastapi import APIRouter, Query, Depends, Body, Request

from ..schemas.reviews_schemas import (
    ReviewsApiResponse,
    MyReviewApiResponse,
    LikeReviewApiResponse,
    CreateReviewApiResponse,
    DeleteReviewApiResponse,
    DeleteReviewLikeApiResponse
)

from ..services.reviews_service import ReviewsService
from ...dependencies.services import get_reviews_service

from ...schemas.error_schema import ApiError


__all__ = ['router', 'public_router']

router = APIRouter(prefix='/reviews', tags=["Reviews"])
public_router = APIRouter(prefix='/reviews', tags=["Reviews"])


@router.post(
    "/createReview/0",
    summary="Отправка или редактирование отзыва",
    description="Отправка или редактирование отзыва о приложение. Отзыв будет опубликован после модерации",
    response_model=CreateReviewApiResponse
)
async def _createReview0(
        request: Request,
        stars: Annotated[int, Query(description="Оценка от 1 до 5", ge=1, le=5)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        text: Annotated[Optional[str], Body(description="Текст отзыва", media_type='text/plain', min_length=1, max_length=512)] = None,
        service: ReviewsService = Depends(get_reviews_service)
) -> CreateReviewApiResponse:
    request.state.session_id = sessionId
    return await service.create_review(sessionId, stars, text)


@router.get(
    "/getMyReview/0",
    summary="Получение своего отзыва",
    description="Получение своего отзыва, если такой есть",
    response_model=MyReviewApiResponse
)
async def _getMyReview0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: ReviewsService = Depends(get_reviews_service)
) -> MyReviewApiResponse:
    request.state.session_id = sessionId
    return await service.get_my_review(sessionId)


@router.delete(
    "/deleteReview/0",
    summary="Удаление отзыва",
    description="Удаление отзыва, если он был ранее опубликован пользователем",
    response_model=DeleteReviewApiResponse
)
async def _deleteReview0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: ReviewsService = Depends(get_reviews_service)
) -> DeleteReviewApiResponse:
    request.state.session_id = sessionId
    return await service.delete_review(sessionId)


@router.get(
    "/getReviews/0",
    summary="Получение отзывов",
    description="Получение отзывов, написанных другими пользователями, с нужной фильтрацией",
    response_model=ReviewsApiResponse
)
async def _getReviews0(
        mode: Annotated[Literal['likes', 'max_stars', 'min_stars'], Query(description="Фильтрация отзывов")] = 'likes',
        offset: Annotated[Optional[int], Query(description="Смещение для получения следующих отзывов", ge=0)] = None,
        limit: Annotated[int, Query(description="Лимит отзывов", ge=1, le=50)] = 16,
        service: ReviewsService = Depends(get_reviews_service)
) -> ReviewsApiResponse:
    return await service.get_reviews(mode, offset, limit)


@router.post(
    "/likeReview/0",
    summary="Поставить реакцию на отзыв",
    description="Поставить реакцию на отзыв, чтобы поднять его в рейтинге",
    response_model=LikeReviewApiResponse
)
async def _likeReview0(
        request: Request,
        reviewId: Annotated[int, Query(description="Идентификатор отзыва", ge=1, le=2**63-1)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: ReviewsService = Depends(get_reviews_service)
) -> LikeReviewApiResponse:
    request.state.session_id = sessionId
    return await service.like_review(sessionId, reviewId)


@public_router.post(
    "/likeReview/0",
    summary="Поставить реакцию на отзыв",
    description="Поставить реакцию на отзыв, чтобы поднять его в рейтинге",
    response_model=LikeReviewApiResponse
)
async def _public_likeReview0(
        request: Request,
        reviewId: Annotated[int, Query(description="Идентификатор отзыва", ge=1, le=2**63-1)],
        csrfToken: Annotated[str, Header(alias='X-CSRF-Token', description="CSRF-токен", min_length=1, max_length=64)],
        service: ReviewsService = Depends(get_reviews_service)
) -> LikeReviewApiResponse:
    csrf_token = request.cookies.get('csrf_token')
    session_id = request.cookies.get('session_id')
    request.state.session_id = session_id
    if csrf_token != csrfToken:
        return LikeReviewApiResponse(
            status=False,
            error=ApiError(
                type="CSRFInvalid"
            )
        )
    if not isinstance(session_id, str):
        return LikeReviewApiResponse(
            status=False,
            error=ApiError(
                type="UnauthorizedError",
                errorMessage="Требуется авторизация. Откройте сайт через приложение"
            )
        )
    return await service.like_review(session_id, reviewId)


@router.delete(
    "/deleteReviewLike/0",
    summary="Удалить реакцию с отзыва",
    description="Удалить ранее поставленную реакцию с отзыва",
    response_model=DeleteReviewLikeApiResponse
)
async def _deleteReviewLike0(
        request: Request,
        reviewId: Annotated[int, Query(description="Идентификатор отзыва", ge=1, le=2**63-1)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: ReviewsService = Depends(get_reviews_service)
) -> DeleteReviewLikeApiResponse:
    request.state.session_id = sessionId
    return await service.delete_review_like(sessionId, reviewId)


@public_router.delete(
    "/deleteReviewLike/0",
    summary="Удалить реакцию с отзыва",
    description="Удалить ранее поставленную реакцию с отзыва",
    response_model=DeleteReviewLikeApiResponse
)
async def _public_deleteReviewLike0(
        request: Request,
        reviewId: Annotated[int, Query(description="Идентификатор отзыва", ge=1, le=2**63-1)],
        csrfToken: Annotated[str, Header(alias='X-CSRF-Token', description="CSRF-токен", min_length=1, max_length=64)],
        service: ReviewsService = Depends(get_reviews_service)
) -> DeleteReviewLikeApiResponse:
    csrf_token = request.cookies.get('csrf_token')
    session_id = request.cookies.get('session_id')
    request.state.session_id = session_id
    if csrf_token != csrfToken:
        return DeleteReviewLikeApiResponse(
            status=False,
            error=ApiError(
                type="CSRFInvalid"
            )
        )
    if not isinstance(session_id, str):
        return DeleteReviewLikeApiResponse(
            status=False,
            error=ApiError(
                type="UnauthorizedError",
                errorMessage="Требуется авторизация. Откройте сайт через приложение"
            )
        )
    return await service.delete_review_like(session_id, reviewId)
