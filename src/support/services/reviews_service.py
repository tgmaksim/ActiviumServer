from typing import Callable, Optional, Literal

from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from dnevnikru import AioDnevnikruApi, BaseDnevnikruException
from firebase.messaging import send_notifications, Notification, AppNotificationChannel

from ..schemas.reviews_schemas import (
    Review,
    ReviewsResult,
    MyReviewResult,
    LikeReviewResult,
    ReviewsApiResponse,
    MyReviewApiResponse,
    LikeReviewApiResponse,
    DeleteReviewLikeResult,
    CreateReviewApiResponse,
    DeleteReviewApiResponse,
    DeleteReviewLikeApiResponse
)

from ...api.session_error import SessionError

from ...dependencies.auth import check_session
from ...models.parent_model import Parent
from ...models.session_model import Session
from ...schemas.error_schema import ApiError

from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['ReviewsService']


class ReviewsService(BaseService[AppUnitOfWork]):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def create_review(self, session_id: str, stars: int, text: Optional[str]) -> CreateReviewApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                person = await dnr.get_person(parent.parent_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            name = person['shortName']

            review = await uow.review_repository.get_review(parent.parent_id)
            if review is None:
                review = await uow.review_repository.create_review(parent.parent_id, name, stars, text, is_open=False)
            else:
                review = await uow.review_repository.update_review(parent.parent_id, name, stars, text, is_open=False)

            await uow.review_repository.check_review(review)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'create_review')

            return CreateReviewApiResponse(
                answer=MyReviewResult(
                    review=Review(
                        reviewId=review.parent_id,
                        name=name,
                        stars=stars,
                        text=text,
                        likes=review.likes,
                        createdAt=review.created_at,
                        isUpdated=review.is_updated
                    ),
                    onModeration=True
                )
            )

    async def resolve_review(self, parent_id: int, publish: bool) -> bool:
        async with self.uow_factory() as uow:
            review = await uow.review_repository.get_review(parent_id)
            if review is None:
                return False

            if publish:
                title = "Отзыв опубликован"
                message = "Ваш отзыв прошел модерацию и теперь доступен к просмотру"
                await uow.review_repository.open_review(parent_id)
            else:
                title = "Отзыв удален"
                message = "Ваш отзыв не прошел модерацию и был удален"
                await uow.review_repository.delete_review(parent_id)

            sessions = await uow.session_repository.get_sessions(parent_id)
            await send_notifications([Notification(
                firebase_token=session.firebase_token,
                title=title,
                message=message,
                channel=AppNotificationChannel.service
            ) for session in sessions if session.firebase_token is not None])

            return publish

    async def get_my_review(self, session_id: str) -> MyReviewApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            review = await uow.review_repository.get_review(parent.parent_id, only_is_open=False)

            return MyReviewApiResponse(
                answer=MyReviewResult(
                    review=Review(
                        reviewId=review.parent_id,
                        name=review.name,
                        stars=review.stars,
                        text=review.text,
                        likes=review.likes,
                        createdAt=review.created_at,
                        isUpdated=review.is_updated
                    ) if review is not None else None,
                    onModeration=review is not None and not review.is_open
                )
            )

    async def delete_review(self, session_id: str) -> DeleteReviewApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            review = await uow.review_repository.get_review(parent.parent_id)
            if review is None:
                return DeleteReviewApiResponse(
                    status=False,
                    error=ApiError(
                        type="ReviewNotFoundError",
                        errorMessage="Вы еще не написали отзыв, чтобы его удалить"
                    )
                )

            await uow.review_repository.delete_review(parent.parent_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'delete_review')

            return DeleteReviewApiResponse()

    async def get_reviews(self, mode: Literal['likes', 'max_stars', 'min_stars'], offset: Optional[int], limit: int) -> ReviewsApiResponse:
        async with self.uow_factory() as uow:
            reviews, _, next_offset = await self.get_top_reviews(uow, mode, offset, limit)

            return ReviewsApiResponse(answer=ReviewsResult(
                reviews=[Review(
                    reviewId=review.parent_id,
                    name=review.name,
                    stars=review.stars,
                    text=review.text,
                    likes=review.likes,
                    createdAt=review.created_at,
                    isUpdated=review.is_updated
                ) for review in reviews],
                nextOffset=next_offset
            ))

    @staticmethod
    async def get_top_reviews(uow: AppUnitOfWork, mode: Literal['likes', 'max_stars', 'min_stars'], offset: Optional[int], limit: int, session: Optional[Session] = None):
        if mode == 'max_stars':
            reviews = await uow.review_repository.get_reviews_by_max_stars(offset, limit + 1)
        elif mode == 'min_stars':
            reviews = await uow.review_repository.get_reviews_by_min_stars(offset, limit + 1)
        else:
            reviews = await uow.review_repository.get_reviews_by_likes(offset, limit + 1)

        next_offset = None
        if len(reviews) == limit + 1:
            reviews.pop()
            next_offset = (offset or 0) + limit

        liked_reviews = set()
        if session:
            reviews_id = list(map(lambda review: review.parent_id, reviews))
            liked_reviews = await uow.review_like_repository.has_my_likes(session.parent_id, reviews_id)

        return reviews, liked_reviews, next_offset

    async def like_review(self, session_id: str, review_id: int) -> LikeReviewApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            review = await uow.review_repository.get_review(review_id)
            if review is None:
                return LikeReviewApiResponse(
                    status=False,
                    error=ApiError(
                        type="ReviewNotFoundError",
                        errorMessage="Отзыв не найден"
                    )
                )

            if review_id == parent.parent_id:
                return LikeReviewApiResponse(
                    status=False,
                    error=ApiError(
                        type="SelfReviewError",
                        errorMessage="Нельзя поставить реакцию на свой отзыв"
                    )
                )

            try:
                await uow.review_like_repository.like_review(parent.parent_id, review_id)
            except IntegrityError:
                return LikeReviewApiResponse(
                    status=False,
                    error=ApiError(
                        type="ReviewLikeAlreadyExistsError",
                        errorMessage="Реакция на данный отзыв уже поставлена"
                    )
                )

            review = await uow.review_repository.like_review(review_id)
            assert review is not None, "review is None"

            await uow.statistic_repository.add_statistic(parent.parent_id, 'like_review')

            return LikeReviewApiResponse(
                answer=LikeReviewResult(
                    review=Review(
                        reviewId=review.parent_id,
                        name=review.name,
                        stars=review.stars,
                        text=review.text,
                        likes=review.likes,
                        createdAt=review.created_at,
                        isUpdated=review.is_updated
                    )
                )
            )

    async def delete_review_like(self, session_id: str, review_id: int) -> DeleteReviewLikeApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            review = await uow.review_repository.get_review(review_id)
            if review is None:
                return DeleteReviewLikeApiResponse(
                    status=False,
                    error=ApiError(
                        type="ReviewNotFoundError",
                        errorMessage="Отзыв не найден"
                    )
                )

            review_like = await uow.review_like_repository.get_like(parent.parent_id, review_id)
            if review_like is None:
                return DeleteReviewLikeApiResponse(
                    status=False,
                    error=ApiError(
                        type="ReviewLikeNotFoundError",
                        errorMessage="Реакция на отзыв не найдена"
                    )
                )

            review = await uow.review_repository.delete_like(review_id)
            assert review is not None, "review is None"
            await uow.review_like_repository.delete_like(parent.parent_id, review_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'delete_review_like')

            return DeleteReviewLikeApiResponse(
                answer=DeleteReviewLikeResult(
                    review=Review(
                        reviewId=review.parent_id,
                        name=review.name,
                        stars=review.stars,
                        text=review.text,
                        likes=review.likes,
                        createdAt=review.created_at,
                        isUpdated=review.is_updated
                    )
                )
            )
