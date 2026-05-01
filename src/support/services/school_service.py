from html import escape
from datetime import timedelta
from typing import Callable, Any, Optional

from yarl import URL
from httpx import AsyncClient
from fastapi import HTTPException

from ...models.session_model import Session
from ...schemas.error_schema import ApiError
from ...config.project_config import settings
from ...dependencies.auth import check_session
from ...dependencies.datetime import astimezone
from ...services.html_response import HtmlResponse

from ..schemas.school_schemas import (
    SchoolPost,
    SchoolPostsResult,
    MarkSchoolPostResult,
    SchoolPostsApiResponse,
    SeeSchoolPostApiResponse,
    ViewSchoolPostApiResponse,
    LikeSchoolPostApiResponse,
    ClickSchoolPostApiResponse,
    UnlikeSchoolPostApiResponse,
    SchoolPostsWithoutVisionResult,
    SchoolPostsWithoutVisionApiResponse,
)

from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['SchoolService']


class SchoolService(BaseService[AppUnitOfWork]):
    """Сервис для взаимодействия с ОО пользователя"""

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def get_post(self, post_id: int) -> HtmlResponse:
        async with self.uow_factory() as uow:
            post = await uow.school_post_repository.get_post(post_id)

            if post is None:
                raise HTTPException(404)

            content = [{
                'type': block['type'],
                'text': self._format_to_html(block['text'], block['entities'])
            } for block in post.content]

            return HtmlResponse(name='post.html', context={
                'title': post.title,
                'description': post.description,
                'has_image': post.has_image,
                'schedule_date': post.schedule_date and post.schedule_date.strftime('%e %b.').strip(),
                'author': post.author,
                'author_verified': post.author_verified,
                'is_updated': post.is_updated,
                'count_viewings': post.count_viewings,
                'count_likes': post.count_likes,
                'content': content,
                'created_at': astimezone(post.created_at, post.timezone).strftime('%e %b. в %H:%M').strip()
            })

    @classmethod
    def _add_surogate(cls, text: str) -> bytes:
        return text.encode("utf-16-le")

    @classmethod
    def _remove_surogate(cls, text: bytes) -> str:
        return text.decode("utf-16-le")

    @classmethod
    def _format_to_html(cls, text: Optional[str], entities: list[dict[str, Any]]) -> Optional[str]:
        if text is None:
            return None

        surogate_text = cls._add_surogate(text)

        tags = {
            'bold': ('<b>', '</b>'),
            'italic': ('<i>', '</i>'),
            'underline': ('<u>', '</u>'),
            'strikethrough': ('<s>', '</s>'),
            'blockquote': ('<blockquote>', '</blockquote>'),
            'expandable_blockquote': ('<blockquote expandable>', '</blockquote>'),
        }

        # (индекс, приоритет, тег)
        events: list[tuple[int, int, str]] = []

        for entity in entities:
            e_type = entity['type']
            start = entity['offset'] * 2
            end = start + entity['length'] * 2

            if e_type == 'url':
                link_text = cls._remove_surogate(surogate_text[start:end])
                open_tag = f"<a href='{escape(link_text)}'>"
                close_tag = "</a>"
            elif e_type == 'text_link':
                open_tag = f"<a href='{escape(entity['url'])}'>"
                close_tag = "</a>"
            elif e_type in tags:
                open_tag, close_tag = tags[e_type]
            else:
                continue

            events.append((start, 1, open_tag))
            events.append((end, 0, close_tag))

        events.sort(key=lambda x: (x[0], x[1]))

        result = []
        last_pos = 0

        for pos, _, tag in events:
            result.append(escape(cls._remove_surogate(surogate_text[last_pos:pos])))
            result.append(tag)
            last_pos = pos

        result.append(escape(cls._remove_surogate(surogate_text[last_pos:])))

        return ''.join(result)

    async def getPosts(self, session_id: str, offset: int) -> SchoolPostsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            limit = 10
            posts = await uow.school_post_repository.get_school_posts(session.active_child.school_id, offset=offset, limit=limit + 1)

            post_ids = [post.post_id for post in posts]

            likes = await uow.school_post_like_repository.has_my_likes(session.parent_id, post_ids)
            my_likes = [like.post_id for like in likes]

            visions = await uow.school_post_vision_repository.has_my_visions(session.parent_id, post_ids)
            my_visions = [vision.post_id for vision in visions]

            next_offset = None
            if len(posts) > limit:
                next_offset = offset + limit

            return SchoolPostsApiResponse(
                answer=SchoolPostsResult(
                    posts=[SchoolPost(
                        postId=post.post_id,
                        title=post.title,
                        description=post.description,
                        imageUrl=str(URL(settings.URL).joinpath('school', 'posts', str(post.post_id), 'image.jpg')) if post.has_image else None,
                        author=post.author,
                        authorVerified=post.author_verified,
                        scheduleDate=post.schedule_date,
                        humanScheduleDate=post.schedule_date and post.schedule_date.strftime('%e %b.').strip(),
                        isUpdated=post.is_updated,
                        countViewings=post.count_viewings,
                        countLikes=post.count_likes,
                        hasMyLike=post.post_id in my_likes,
                        isSaw=post.post_id in my_visions,
                        createdAt=post.created_at,
                        humanCreatedAt=astimezone(post.created_at, post.timezone).strftime('%e %b. в %H:%M').strip(),
                        postUrl=str(URL(settings.URL).joinpath('school', 'posts', str(post.post_id)))
                    ) for i, post in enumerate(posts) if i < limit],
                    nextOffset=next_offset
                )
            )

    async def checkNewPosts(self, session_id: str) -> SchoolPostsWithoutVisionApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            return SchoolPostsWithoutVisionApiResponse(
                answer=SchoolPostsWithoutVisionResult(
                    countPosts=await self._check_new_posts(uow, session)
                )
            )

    @classmethod
    async def _check_new_posts(cls, uow: AppUnitOfWork, session: Session) -> int:
        posts = await uow.school_post_repository.get_school_posts(session.active_child.school_id, last=timedelta(days=14))
        saw_posts = await uow.school_post_vision_repository.has_my_visions(session.parent_id, [post.post_id for post in posts])

        return len(posts) - len(saw_posts)

    @classmethod
    async def _get_post(cls, post_id: int, uow: AppUnitOfWork, session: Session):
        post = await uow.school_post_repository.get_post(post_id)
        assert post is not None, "post is None"

        post_ids = [post_id]

        likes = await uow.school_post_like_repository.has_my_likes(session.parent_id, post_ids)
        my_likes = [like.post_id for like in likes]

        visions = await uow.school_post_vision_repository.has_my_visions(session.parent_id, post_ids)
        my_visions = [vision.post_id for vision in visions]

        image_url = None
        if post.has_image:
            image_url = str(URL(settings.URL).joinpath('school', 'posts', str(post.post_id), 'image.jpg'))

        return SchoolPost(
            postId=post.post_id,
            title=post.title,
            description=post.description,
            imageUrl=image_url,
            author=post.author,
            authorVerified=post.author_verified,
            scheduleDate=post.schedule_date,
            humanScheduleDate=post.schedule_date and post.schedule_date.strftime('%e %b.').strip(),
            isUpdated=post.is_updated,
            countViewings=post.count_viewings,
            countLikes=post.count_likes,
            hasMyLike=post.post_id in my_likes,
            isSaw=post.post_id in my_visions,
            createdAt=post.created_at,
            humanCreatedAt=astimezone(post.created_at, post.timezone).strftime('%e %b. в %H:%M').strip(),
            postUrl=str(URL(settings.URL).joinpath('school', 'posts', str(post.post_id)))
        )

    async def seePost(self, session_id: str, post_id: int) -> SeeSchoolPostApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            post = await uow.school_post_repository.get_post(post_id)
            if post is None:
                await uow.log_repository.add_log(
                    path='seePost',
                    session_id=session_id,
                    status=False,
                    value=f"Пост {post_id} не найден"
                )
                return SeeSchoolPostApiResponse(
                    status=False,
                    error=ApiError(
                        type="SchoolPostNotFoundError",
                        errorMessage="Пост не найден"
                    )
                )

            await self._see_post(post_id, uow, session)

            return SeeSchoolPostApiResponse(
                answer=MarkSchoolPostResult(
                    post=await self._get_post(post_id, uow, session),
                    countPostsWithoutVision=await self._check_new_posts(uow, session)
                )
            )

    @classmethod
    async def _see_post(cls, post_id: int, uow: AppUnitOfWork, session: Session):
        vision = await uow.school_post_vision_repository.get_vision(session.parent_id, post_id)
        if vision is None:
            await uow.school_post_vision_repository.see_post(session.parent_id, post_id)
            await uow.school_post_repository.see_post(post_id)

    async def clickPost(self, session_id: str, post_id: int) -> ClickSchoolPostApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            post = await uow.school_post_repository.get_post(post_id)
            if post is None:
                await uow.log_repository.add_log(
                    path='clickPost',
                    session_id=session_id,
                    status=False,
                    value=f"Пост {post_id} не найден"
                )
                return ClickSchoolPostApiResponse(
                    status=False,
                    error=ApiError(
                        type="SchoolPostNotFoundError",
                        errorMessage="Пост не найден"
                    )
                )

            await self._see_post(post_id, uow, session)
            await self._click_post(post_id, uow, session)

            return ClickSchoolPostApiResponse(
                answer=MarkSchoolPostResult(
                    post=await self._get_post(post_id, uow, session),
                    countPostsWithoutVision=await self._check_new_posts(uow, session)
                )
            )

    @classmethod
    async def _click_post(cls, post_id: int, uow: AppUnitOfWork, session: Session):
        click = await uow.school_post_click_repository.get_click(session.parent_id, post_id)
        if click is None:
            await uow.school_post_click_repository.click_post(session.parent_id, post_id)
            await uow.school_post_repository.click_post(post_id)

    async def viewPost(self, session_id: str, post_id: int) -> ViewSchoolPostApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            post = await uow.school_post_repository.get_post(post_id)
            if post is None:
                await uow.log_repository.add_log(
                    path='viewPost',
                    session_id=session_id,
                    status=False,
                    value=f"Пост {post_id} не найден"
                )
                return ViewSchoolPostApiResponse(
                    status=False,
                    error=ApiError(
                        type="SchoolPostNotFoundError",
                        errorMessage="Пост не найден"
                    )
                )

            await self._see_post(post_id, uow, session)
            await self._click_post(post_id, uow, session)
            await self._view_post(post_id, uow, session)

            return ViewSchoolPostApiResponse(
                answer=MarkSchoolPostResult(
                    post=await self._get_post(post_id, uow, session),
                    countPostsWithoutVision=await self._check_new_posts(uow, session)
                )
            )

    @classmethod
    async def _view_post(cls, post_id: int, uow: AppUnitOfWork, session: Session):
        view = await uow.school_post_viewing_repository.get_view(session.parent_id, post_id)
        if view is None:
            await uow.school_post_viewing_repository.view_post(session.parent_id, post_id)
            await uow.school_post_repository.view_post(post_id)

    async def likePost(self, session_id: str, post_id: int) -> LikeSchoolPostApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            post = await uow.school_post_repository.get_post(post_id)
            if post is None:
                await uow.log_repository.add_log(
                    path='likePost',
                    session_id=session_id,
                    status=False,
                    value=f"Пост {post_id} не найден"
                )
                return LikeSchoolPostApiResponse(
                    status=False,
                    error=ApiError(
                        type="SchoolPostNotFoundError",
                        errorMessage="Пост не найден"
                    )
                )

            await self._see_post(post_id, uow, session)
            await self._click_post(post_id, uow, session)
            await self._view_post(post_id, uow, session)
            await self._like_post(post_id, uow, session)

            return LikeSchoolPostApiResponse(
                answer=MarkSchoolPostResult(
                    post=await self._get_post(post_id, uow, session),
                    countPostsWithoutVision=await self._check_new_posts(uow, session)
                )
            )

    @classmethod
    async def _like_post(cls, post_id: int, uow: AppUnitOfWork, session: Session):
        like = await uow.school_post_like_repository.get_like(session.parent_id, post_id)
        if like is None:
            await uow.school_post_like_repository.like_post(session.parent_id, post_id)
            await uow.school_post_repository.like_post(post_id)

    async def unlikePost(self, session_id: str, post_id: int) -> UnlikeSchoolPostApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            post = await uow.school_post_repository.get_post(post_id)
            if post is None:
                await uow.log_repository.add_log(
                    path='unlikePost',
                    session_id=session_id,
                    status=False,
                    value=f"Пост {post_id} не найден"
                )
                return UnlikeSchoolPostApiResponse(
                    status=False,
                    error=ApiError(
                        type="SchoolPostNotFoundError",
                        errorMessage="Пост не найден"
                    )
                )

            await self._see_post(post_id, uow, session)
            await self._click_post(post_id, uow, session)
            await self._view_post(post_id, uow, session)
            await self._unlike_post(post_id, uow, session)

            return UnlikeSchoolPostApiResponse(
                answer=MarkSchoolPostResult(
                    post=await self._get_post(post_id, uow, session),
                    countPostsWithoutVision=await self._check_new_posts(uow, session)
                )
            )

    @classmethod
    async def _unlike_post(cls, post_id: int, uow: AppUnitOfWork, session: Session):
        like = await uow.school_post_like_repository.get_like(session.parent_id, post_id)
        if like is not None:
            await uow.school_post_like_repository.delete_like(session.parent_id, post_id)
            await uow.school_post_repository.unlike_post(post_id)
