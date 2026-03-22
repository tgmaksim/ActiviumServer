import secrets

from typing import Optional

from .reviews_service import ReviewsService
from ...services.html_response import HtmlResponse

from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['SiteService']


class SiteService(BaseService[AppUnitOfWork]):
    async def get_root(self, session_id: Optional[str], likes_offset: Optional[int], likes_sort: Optional[str]) -> HtmlResponse:
        async with self.uow_factory() as uow:
            session = None
            if isinstance(session_id, str):
                session = await uow.session_repository.get_session(session_id)

            latest = await uow.version_repository.get_latest_version()
            previous_versions = await uow.version_repository.get_all_versions()

            mode = 'likes'
            if likes_sort in ('likes', 'max_stars', 'min_stars'):
                mode = likes_sort

            offset = 0
            if isinstance(likes_offset, int) and likes_offset >= 0:
                offset = likes_offset

            limit = 3 if offset == 0 else 10

            reviews, liked_reviews, next_offset = await ReviewsService.get_top_reviews(uow, mode, offset, limit, session)
            csrf_token = secrets.token_urlsafe(32)

            await uow.statistic_repository.add_statistic(session and session.parent_id, 'site')

            return HtmlResponse(
                name='main.html',
                context={
                    'version': "0.0.1" if latest is None else latest.version,
                    'date': '' if latest is None else latest.date,
                    'version_status': "Небольшие улучшения" if latest is None else latest.status,
                    'update_log': [] if latest is None else latest.logs.split('\n'),
                    'previous_versions': [{
                        'version': v.version,
                        'date': v.date,
                        'status': v.status,
                        'update_log': v.logs.split('\n'),
                    } for v in previous_versions],
                    'reviews': [{
                        'id': review.parent_id,
                        'author': review.name,
                        'stars': review.stars,
                        'text': review.text,
                        'has_my_like': review.parent_id in liked_reviews,
                        'reactions': review.likes,
                        'created_at': review.created_at.strftime('%d.%m.%Y'),
                        'is_edited': review.is_updated
                    } for review in reviews],
                    'next_likes_offset': next_offset,
                    'likes_sort': mode,
                    'csrf_token': csrf_token
                },
                cookies={
                    'key': 'csrf_token',
                    'value': csrf_token,
                    'httponly': False,
                    'samesite': 'lax'
                }
            )
